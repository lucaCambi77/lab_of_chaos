# Example on how to use an Apollo Server and fetch data from different Apis

## Requirements

- Nodejs

## Build the application

- `npm install`

## Start the application

- `node index.js`

This will start an Apollo server at http://localhost:4000

## Data Model and Apollo

We create two different express server to simulate different databases using in memory posts and comments of a social-like application example.

Post example:

```json
{
  "id": 1,
  "title": "Some title"
}
```

Comment example:

```json
{
  "id": 1,
  "postId": [
    1
  ],
  "comment": "some comment"
}
```

After we start the application, we can query the Apollo server:

```graphql
query GetPosts {
  posts {
    id
    title
    comments {
      comment
    }
  }
}
```

This works by defining `types` and `resolvers` in the graphql schema, [view the apollo file](./apollo.js)

## Different approaches

The Post entity has a reference to the comment id(s) while Comment keeps a reference to the post id(s). Therefore, there are 2 different approaches to query the data:

1) Resolve the comments by the comment ids of the post
2) Resolve the comments by the post id (This would also allow, in theory, not to store the comment ids for a Post)