const posts = [
    {
        id: 1,
        title: "Post 1",
        user: "user1",
        comments: [1, 2]
    },
    {
        id: 2,
        title: "Post 2",
        user: "user2",
        comments: [3]
    }
]

const postComments = [
    {
        id: 1,
        postId: 1,
        user: "user3",
        comment: "Well Done!",
    },
    {
        id: 3,
        postId: 2,
        user: "user4",
        comment: "Very very well!",
    },
    {
        id: 2,
        postId: 1,
        user: "user5",
        comment: "Don't dig it!",
    }
]

module.exports = {posts, postComments}