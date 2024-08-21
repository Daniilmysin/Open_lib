import pytest
from unittest.mock import AsyncMock, patch
from DBScripts import BookAct
BookAdd = BookAct().BookAdd

@pytest.fixture
def book_add():
    return BookAdd()


@pytest.mark.asyncio
async def test_author_id_existing_author(book_add):
    book_add.find_author = AsyncMock(return_value=True)
    book_add.set_data = AsyncMock(return_value=True)

    result = await book_add.author_id(1, 1)

    assert result is True
    book_add.find_author.assert_awaited_once_with(1)
    book_add.set_data.assert_awaited_once_with(1, {"author": 1})


@pytest.mark.asyncio
async def test_author_id_non_existing_author(book_add):
    book_add.find_author = AsyncMock(return_value=None)

    result = await book_add.author_id(1, 1)

    assert result is None
    book_add.find_author.assert_awaited_once_with(1)
    book_add.set_data.assert_not_called()


@pytest.mark.asyncio
async def test_name(book_add):
    book_add.get_data = AsyncMock(return_value={})
    book_add.set_data = AsyncMock(return_value=True)

    result = await book_add.name(1, "New Book")

    assert result is True
    book_add.get_data.assert_awaited_once_with(1)
    book_add.set_data.assert_awaited_once_with(1, {'name': "New Book"})


@pytest.mark.asyncio
async def test_description(book_add):
    book_add.get_data = AsyncMock(return_value={})
    book_add.set_data = AsyncMock(return_value=True)

    result = await book_add.description(1, "Description of the book")

    assert result is True
    book_add.get_data.assert_awaited_once_with(1)
    book_add.set_data.assert_awaited_once_with(1, {'description': "Description of the book"})


@pytest.mark.asyncio
async def test_photo(book_add):
    book_add.get_data = AsyncMock(return_value={})
    book_add.set_data = AsyncMock(return_value=True)

    result = await book_add.photo(1, "photo.jpg")

    assert result is True
    book_add.get_data.assert_awaited_once_with(1)
    book_add.set_data.assert_awaited_once_with(1, {'photo': "photo.jpg"})


@pytest.mark.asyncio
@patch("your_module.AsyncSession")
async def test_end_success(mock_async_session, book_add):
    book_add.get_data = AsyncMock(return_value={
        "author": 1,
        "name": "New Book",
        "description": "Description",
        "photo": "photo.jpg"
    })
    book_add.find_user = AsyncMock(return_value="UserObject")
    book_add.find_author = AsyncMock(return_value="AuthorObject")
    book_add.del_data = AsyncMock()

    mock_session_instance = mock_async_session.return_value.__aenter__.return_value
    mock_session_instance.commit = AsyncMock()

    result = await book_add.end(1, "book.epub")

    assert result is True
    book_add.get_data.assert_awaited_once_with(1)
    book_add.find_user.assert_awaited_once_with(1)
    book_add.find_author.assert_awaited_once_with(1)
    book_add.del_data.assert_awaited_once_with(1)
    mock_session_instance.add.assert_called_once()
    mock_session_instance.commit.assert_awaited_once()


@pytest.mark.asyncio
@patch("your_module.AsyncSession")
async def test_end_no_user(mock_async_session, book_add):
    book_add.get_data = AsyncMock(return_value={
        "author": 1,
        "name": "New Book",
        "description": "Description",
        "photo": "photo.jpg"
    })
    book_add.find_user = AsyncMock(return_value=None)

    result = await book_add.end(1, "book.epub")

    assert result is None
    book_add.get_data.assert_awaited_once_with(1)
    book_add.find_user.assert_awaited_once_with(1)
    mock_async_session.assert_not_called()
