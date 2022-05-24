import time
from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from app.utils.my_posts import my_posts
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    """Model of a post body"""

    title: str
    content: str
    published: bool = True
    likes = 0


# Database connection
while True:
    try:
        conn = psycopg2.connect(
            dbname="fast-backend",
            user="postgres",
            password="postgres",
            host="localhost",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Connected to the database")
        break
    except Exception as error:
        print("I am unable to connect to the database")
        print(f"ERROR:-  {error}")
        time.sleep(2)


def find_post(id):
    """
    The find_post function searches the list of posts
    for a post with the given id.
    If it finds that post, it returns that post's dictionary;
    otherwise, it returns None.

    :param id: Find the post with a specific id
    :return: A dictionary
    """

    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id: int):
    """
    The find_index_post function finds the index of a post in my_posts that
    has the same id as the parameter id.
       If no such post exists, it returns None.

    :param id:int: Specify the id of the post we want to find
    :return: The index of the post in my_posts that has an id
    equal to the value of id
    """
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to my api!!"}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    """
    The get_posts function returns all the posts in the database.

    :param db:Session=Depends(get_db): Pass the database session
    to the function
    :return: A list of all the posts in the database
    """

    # RAW_SQL
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    """
    The create_posts function creates a new post in the database.
    It takes as input a Post object and returns the created post.

    :param post:Post: Pass in the data from the api request
    :param db:Session=Depends(get_db): Inject the database session dependency
    into the function
    :return: A post object
    """

    #  Works BUT Vulnerable to SQL Injection 👀
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES
    #     (post.title, post.content, post.published, post.likes)"""
    # )

    # RAW SQL
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) /
    #     VALUES (%s, %s, %s) RETURNING *""",
    #     (post.title, post.content, post.published),
    # )
    # conn.commit()

    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    """
    The get_post function returns a post with the given id.

    :param post_id:int: Capture the id of the post we want to retrieve
    :param db:Session=Depends(get_db): Inject the database session 
    into the function
    :return: A tuple with one element, the post with the given id
    """

    # RAW SQL
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(post_id),))
    # post = (cursor.fetchone(),)
    post = db.query(models.Post).filter(models.Post.post_id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return {"post_detail": post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """
    The delete_post function will delete a post from the database.
    It will return the deleted post object on success
    or an error message if it fails.

    :param post_id:int: Specify the id of the post to be deleted
    :param db:Session=Depends(get_db): Pass the database session to function
    :return: A dictionary with the id of the deleted post
    :doc-author: Trelent
    """

    # cursor.execute(
    #     """DELETE FROM posts WHERE/
    #                id = %s RETURNING *""",
    #     (str(post_id),),
    # )
    # deleted_post = cursor.fetchone()
    # conn.commit()
    deleted_post = db.query(models.Post).filter(models.Post.post_id == post_id)
    if deleted_post.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id-{post_id} not found",
        )
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post, db: Session = Depends(get_db)):

    # RAW SQL
    # cursor.execute(
    #     """UPDATE posts SET title = %s, content = %s, published = %s /
    #     WHERE id = %s RETURNING *""",
    #     (
    #         post.title,
    #         post.content,
    #         post.published,
    #         str(post_id),
    #     ),
    # )
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.post_id == post_id)
    updated_post = post_query.first()
    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id-{post_id} not found",
        )

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return {"data": post_query.first()}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}
