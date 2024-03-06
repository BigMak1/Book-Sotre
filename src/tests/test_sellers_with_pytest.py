import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers


@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Maxim", 
            "last_name": "Konovalov",
            "email": "mkonovalov@mail.ru", 
            "password": "qwerty"}

    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": result_data["id"],
        "first_name": "Maxim",
        "last_name": "Konovalov",
        "email": "mkonovalov@mail.ru",
    }


@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):

    seller = sellers.Seller(first_name="Maxim", last_name="Konovalov", email="mkonovalov@mail.ru", password="qwerty")
    seller_2 = sellers.Seller(first_name="Anton", last_name="Antonov", email="anton444@mail.ru", password="abcde")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2 

    assert response.json() == {
        "sellers": [
            {"id": seller.id, "first_name": "Maxim", "last_name": "Konovalov", "email": "mkonovalov@mail.ru"},
            {"id": seller_2.id, "first_name": "Anton", "last_name": "Antonov", "email": "anton444@mail.ru"}
        ]
    }


@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Maxim", last_name="Konovalov", email="mkonovalov@mail.ru", password="qwerty")
    seller_2 = sellers.Seller(first_name="Anton", last_name="Antonov", email="anton444@mail.ru", password="abcde")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "id": seller.id,
        "first_name": "Maxim",
        "last_name": "Konovalov",
        "email": "mkonovalov@mail.ru",
        "books": [
            {
                "id": book.id,
                "author": "Pushkin",
                "title": "Eugeny Onegin",
                "year": 2001,
                "count_pages": 104,
                "seller_id": seller.id,
            }
        ],
    }


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Maxim", last_name="Konovalov", email="mkonovalov@mail.ru", password="qwerty")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Maxim", last_name="Konovalov", email="mkonovalov@mail.ru", password="qwerty")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
            f"/api/v1/sellers/{seller.id}",
            json={
                "id": seller.id,
                "first_name": "Anton",
                "last_name": "Antonov",
                "email": "anton444@mail.ru",
                "password": "abcde",
            },
        )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(sellers.Seller, seller.id)
    assert res.id == seller.id
    assert res.first_name == "Anton"
    assert res.last_name == "Antonov"
    assert res.email == "anton444@mail.ru"