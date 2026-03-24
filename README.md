Task 11: Quick Guide
Product Pagination

The API now supports pagination to handle large numbers of products efficiently.

How to use:

    limit: The number of products to return (default is 10).

    offset: The starting point, used to skip a specific number of products (default is 0).

Examples:

    To get the first 10 products: GET /products

    To get 5 products starting from the 11th one: GET /products?limit=5&offset=10

Soft Delete

Products marked as deleted (is_deleted = True) will no longer appear in the list.

Benefit: This improves system performance and reduces the load on the server and browser, while keeping the data safe in the database.
