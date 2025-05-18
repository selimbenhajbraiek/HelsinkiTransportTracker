    
from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import asyncpg
from contextlib import asynccontextmanager
from typing import Optional
import asyncio
import httpx

DATABASE_URL = "postgresql://selimbraiek:selimselim@localhost:5432/helsenki_db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await asyncpg.create_pool(DATABASE_URL)
    asyncio.create_task(auto_sync_loop())
    asyncio.create_task(auto_station_sync_loop())
    yield
    await app.state.db.close()
       

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home():
    return FileResponse("static/index.html")

@app.get("/api/vehicles")
async def get_all_vehicles():
    rows = await app.state.db.fetch("SELECT * FROM vehicles")
    result = []
    for row in rows:
        record = dict(row)
        if isinstance(record.get("timestamp"), datetime):
            record["timestamp"] = record["timestamp"].isoformat()
        result.append(record)
    return JSONResponse(result)


@app.get("/dashboard")
async def dashboard():
    return FileResponse("static/dashboard.html")

@app.get("/api/stats/by_type")
async def by_type():
    query = "SELECT type, COUNT(*) as count FROM vehicles GROUP BY type"
    rows = await app.state.db.fetch(query)
    return JSONResponse([
        {"details": {"mode": row["type"]}, "count": row["count"]} for row in rows
    ])

@app.get("/api/stats/hourly")
async def hourly(date: str):
    from datetime import datetime
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return JSONResponse({"error": "Invalid date format"}, status_code=400)

    query = """
        SELECT date_trunc('hour', timestamp) as timestamp, COUNT(*) as count
        FROM vehicles
        WHERE DATE(timestamp) = $1
        GROUP BY timestamp
        ORDER BY timestamp
    """
    rows = await app.state.db.fetch(query, target_date)

    result = []
    for r in rows:
        record = dict(r)
        record["timestamp"] = record["timestamp"].isoformat()
        result.append(record)

    return JSONResponse(result)

@app.get("/api/stats/daily")
async def daily(start_date: str, end_date: str):
    # Convert input strings to date objects
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return JSONResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status_code=400)

    query = """
        SELECT DATE(timestamp) as timestamp, COUNT(*) as count
        FROM vehicles
        WHERE DATE(timestamp) BETWEEN $1 AND $2
        GROUP BY timestamp
        ORDER BY timestamp
    """
    rows = await app.state.db.fetch(query, start, end)
    result = []
    for r in rows:
        record = dict(r)
        if isinstance(record["timestamp"], datetime):
            record["timestamp"] = record["timestamp"].isoformat()
        elif hasattr(record["timestamp"], "isoformat"):
            record["timestamp"] = record["timestamp"].isoformat()
        result.append(record)
    return JSONResponse(result)

@app.get("/api/stats/by_station")
async def top_stations(limit: int = 10):
    query = """
        SELECT s.station_name, COUNT(*) as count
        FROM vehicles v
        JOIN stations s ON v.station_id = s.id
        GROUP BY s.station_name
        ORDER BY count DESC
        LIMIT $1
    """
    rows = await app.state.db.fetch(query, limit)
    return JSONResponse([
        {"details": {"station_name": row["station_name"]}, "count": row["count"]} for row in rows
    ])

@app.get("/api/stations/search")
async def search_stations(query: str = Query(..., min_length=1)):
    rows = await app.state.db.fetch(
        """
        SELECT id, station_name AS name, latitude, longitude, zone_id 
        FROM stations 
        WHERE station_name ILIKE $1
        """,
        f"%{query}%"
    )
    return JSONResponse([dict(r) for r in rows])

@app.get("/api/station/{station_id}")
async def station_detail(station_id: int):
    row = await app.state.db.fetchrow(
        """
        SELECT id, station_name AS name, zone_id, platform_code, latitude, longitude 
        FROM stations 
        WHERE id = $1
        """,
        station_id
    )
    if row:
        data = dict(row)
        data["position"] = {
            "lat": float(data.pop("latitude")),
            "lng": float(data.pop("longitude"))
        }
        data["routes"] = [f"R{station_id % 4 + 1}"]
        return JSONResponse(data)
    return JSONResponse({"error": "Station not found"}, status_code=404)


@app.get("/api/stations/route")
async def station_route(from_station: str, to_station: str):
    query = """
        SELECT station_name, latitude, longitude
        FROM stations
        WHERE station_name ILIKE $1 OR station_name ILIKE $2
    """
    rows = await app.state.db.fetch(query, from_station, to_station)

    if len(rows) != 2:
        return JSONResponse({"error": "One or both stations not found"}, status_code=404)

    return JSONResponse([dict(row) for row in rows])



    

async def auto_sync_loop():
    await asyncio.sleep(3)
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://render-cloud-o6dk.onrender.com/live/vehicles")
                response.raise_for_status()
                data = response.json()
                print(f"[SYNC] Fetched {len(data)} entries from cloud.")
        except Exception as e:
            print(f"[Sync Error] {e}")
            await asyncio.sleep(10)
            continue

        for entry in data:
            try:
                ts = entry["timestamp"]
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)

                await app.state.db.execute("""
                    INSERT INTO vehicles (type, station_id, timestamp, status)
                    SELECT $1::VARCHAR, $2::INT, $3::TIMESTAMP, $4::VARCHAR
                    WHERE NOT EXISTS (
                        SELECT 1 FROM vehicles
                        WHERE type = $1::VARCHAR AND station_id = $2::INT AND timestamp = $3::TIMESTAMP
                    )
                """, entry["type"], entry["station_id"], ts, entry.get("status", "ACTIVE"))

                print(f"[INSERTED] {entry['type']} at station {entry['station_id']}")

            except Exception as e:
                print(f"[Insert Error] {e}")
                continue

        await asyncio.sleep(5)


async def auto_station_sync_loop():
    await asyncio.sleep(3)
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://render-cloud-o6dk.onrender.com/live/stations")  
                response.raise_for_status()
                data = response.json()
                print(f"[STATION SYNC] Fetched {len(data)} stations from cloud.")
        except Exception as e:
            print(f"[Station Sync Error] {e}")
            await asyncio.sleep(10)
            continue

        for entry in data:
            try:
                await app.state.db.execute("""
                    INSERT INTO stations (station_name, platform_code, zone_id, longitude, latitude)
                    SELECT $1::VARCHAR, $2::VARCHAR, $3::VARCHAR, $4::DOUBLE PRECISION, $5::DOUBLE PRECISION
                    WHERE NOT EXISTS (
                        SELECT 1 FROM stations
                        WHERE station_name = $1::VARCHAR AND platform_code = $2::VARCHAR
                    )
                """,
                entry["station_name"],
                entry.get("platform_code"),
                entry.get("zone_id"),
                float(entry["longitude"]),
                float(entry["latitude"]))

                print(f"[STATION INSERTED] {entry['station_name']}")

            except Exception as e:
                print(f"[Station Insert Error] {e}")
                continue

        await asyncio.sleep(5)
