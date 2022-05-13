from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from typing import Optional
from random import randint

app = FastAPI()


class Post(BaseModel):
    """Model of a post body"""

    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_posts = [
    {
        "id": 1,
        "title": "My first post",
        "content": "This is my first post",
        "published": True,
        "rating": 1,
    },
    {
        "id": 2,
        "title": "My second post",
        "content": "This is my second post",
        "published": True,
        "rating": 2,
    },
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id: int):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to my api!!"}


@app.get("/posts")
def get_posts():
    """
    The get_posts function returns a list of all the blog posts.
    :return: A list of dictionaries
    """
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = dict(post)
    post_dict["id"] = randint(1, 10000)
    my_posts.append(post_dict)
    return {"data": post}


@app.get("/posts/{post_id}")
def get_post(post_id: int, response: Response):
    """The get_post function returns a post with the given id.
    :param post_id: Specify the id [int] of the post that we want to retrieve
    :param response:Response: Return the response object
    :return: The post with the id passed in"""

    post = find_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return {"post_detail": post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    """The delete_post function removes a post from the list of posts.
    Parameters:
        post_id (int): The id of the post to be deleted."""

    index = find_index_post(post_id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id-{post_id} not found",
        )
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):
    """
    The update_post function updates a post in the my_posts list.
    It takes two arguments:
        -post_id: an integer representing the id of the post to be updated, and
        -post: a Post object containing all of the information needed to update that particular post.

       It returns None.

    :param post_id:int: Find the index of the post in my_posts
    :param post:Post: Create a new post
    :return: The new post with the updated information
    """

    index = find_index_post(post_id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id-{post_id} not found",
        )
    post_dict = post.dict()
    print(post_dict)
    post_dict["id"] = post_id
    my_posts[index] = post_dict

    return {"data": post_dict}
