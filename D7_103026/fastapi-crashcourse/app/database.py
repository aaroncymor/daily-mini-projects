from app.schemas import MediaType

# In-memory database dictionary
fake_db: dict[int, dict] = {
    1: {
        "id": 1,
        "title": "Frieren: Beyond Journey's End",
        "media_type": MediaType.ANIME,
        "rating": 9.3
    },
    2: {
        "id": 2,
        "title": "Orb: On the Movements of the Earth",
        "media_type": MediaType.ANIME,
        "rating": 9.6
    },
    3: {
        "id": 3,
        "title": "Delicious in Dungeon",
        "media_type": MediaType.MANGA,
        "rating": 9.0
    },
}


# Dependency function to get DB context
def get_db():
    return fake_db
