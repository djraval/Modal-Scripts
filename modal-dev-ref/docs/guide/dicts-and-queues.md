# Dicts and Queues

Modal provides a variety of distributed objects to enable seamless
interactivity and data transfer across different components of a distributed
system. Two key objects are dicts and queues, both of which serve specific
roles in facilitating communication and data management in your applications.

## Modal Dicts

A Dict in Modal provides distributed key-value storage. Much like a standard
Python dictionary, it lets you store and retrieve values using keys. However,
unlike a regular dictionary, a Dict in Modal is shared across all containers
of an application and can be accessed and manipulated concurrently from any of
them.

    
    
    import modal
    
    app = modal.App()
    
    # Create a persisted dict - the data gets retained between app runs
    my_dict = modal.Dict.from_name("my-persisted-dict", create_if_missing=True)
    
    
    @app.local_entrypoint()
    def main():
        my_dict["key"] = "value"  # setting a value
        value = my_dict["key"]    # getting a value

Copy

Dicts in Modal are persisted, which means that the data in the dictionary is
stored and can be retrieved later, even after the application is redeployed.
They can also be accessed from other Modal functions.

You can store Python values of any type within Dicts, since they’re serialized
using `cloudpickle`. Note that you will need to have the library defining the
type installed in the environment where you retrieve the object from the Dict,
otherwise a `DeserializationError` will be raised.

Unlike with normal Python dictionaries, updates to mutable value types will
not be reflected in other containers unless the updated object is explicitly
put back into the Dict. As a consequence, patterns like chained updates
(`my_dict["outer_key"]["inner_key"] = value`) cannot be used the same way as
they would with a local dictionary.

Currently, the ​overall​ size of a Dict is limited to 10 GiB. However, we
intend to lower this limit as Dicts are not intended for caching large
datasets. The per-object size limit is 100 MiB and the maximum number of
entries per update request is 10,000.

## Modal Queues

A Queue in Modal is a distributed queue-like object. It allows you to add and
retrieve items in a first-in-first-out (FIFO) manner. Queues are particularly
useful when you want to handle tasks or process data asynchronously, or when
you need to pass messages between different components of your distributed
system.

    
    
    import modal
    
    app = modal.App()
    my_queue = modal.Queue.from_name("my-persisted-queue", create_if_missing=True)
    
    
    @app.local_entrypoint()
    def main():
        my_queue.put("some object")  # adding a value
        value = my_queue.get()  # retrieving a value

Copy

Similar to Dicts, Queues are also persisted and support values of any type.

### Queue partitions

Queues are split into separate FIFO partitions via a string key. By default,
one partition (corresponding to an empty key) is used.

A single `Queue` can contain up to 100,000 partitions, each with up to 5,000
items. Each item can be up to 1 MiB. These limits also apply to the default
partition.

    
    
    import modal
    
    app = modal.App()
    my_queue = modal.Queue.from_name("my-persisted-queue", create_if_missing=True)
    
    
    @app.local_entrypoint()
    def main():
        my_queue.put("some value")
        my_queue.put(123)
    
        assert my_queue.get() == "some value"
        assert my_queue.get() == 123
    
        my_queue.put(0)
        my_queue.put(1, partition="foo")
        my_queue.put(2, partition="bar")
    
        # Default and "foo" partition are ignored by the get operation.
        assert my_queue.get(partition="bar") == 2
    
        # Set custom 10s expiration time on "foo" partition.
        my_queue.put(3, partition="foo", partition_ttl=10)
    
        # (beta feature) Iterate through items in place (read immutably)
        my_queue.put(1)
        assert [v for v in my_queue.iterate()] == [0, 1]

Copy

By default, each partition is cleared 24 hours after the last `put` operation.
A lower TTL can be specified by the `partition_ttl` argument in the `put` or
`put_many` methods. Each partition’s expiry is handled independently.

As such, `Queue`s are best used for communication between active functions and
not relied on for persistent storage.

## Asynchronous calls

Both Dicts and Queues are synchronous by default, but they support
asynchronous interaction with the `.aio` function suffix.

    
    
    @app.local_entrypoint()
    async def main():
        await my_queue.put.aio(100)
        assert await my_queue.get.aio() == 100
    
        await my_dict.put.aio("hello", 400)
        assert await my_dict.get.aio("hello") == 400

Copy

Note that `.put` and `.get` are aliases for the overloaded indexing operators
on Dicts, but you need to invoke them by name for asynchronous calls.

Please see the docs on asynchronous functions for more information.

## Example: Dict and Queue Interaction

To illustrate how dicts and queues can interact together in a simple
distributed system, consider the following example program that crawls the
web, starting from wikipedia.org and traversing links to many sites in
breadth-first order. The Queue stores pages to crawl, while the Dict is used
as a kill switch to stop execution of tasks immediately upon completion.

    
    
    import queue
    import sys
    from datetime import datetime
    
    import modal
    
    
    app = modal.App(image=modal.Image.debian_slim().pip_install("requests", "beautifulsoup4"))
    
    
    def extract_links(url: str) -> list[str]:
        """Extract links from a given URL."""
        import requests
        import urllib.parse
        from bs4 import BeautifulSoup
    
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for link in soup.find_all("a"):
            links.append(urllib.parse.urljoin(url, link.get("href")))
        return links
    
    
    @app.function()
    def crawl_pages(q: modal.Queue, d: modal.Dict, urls: set[str]) -> None:
        for url in urls:
            if "stop" in d:
                return
            try:
                s = datetime.now()
                links = extract_links(url)
                print(f"Crawled: {url} in {datetime.now() - s}, with {len(links)} links")
                q.put_many(links)
            except Exception as exc:
                print(f"Failed to crawl: {url} with error {exc}, skipping...", file=sys.stderr)
    
    
    @app.function()
    def scrape(url: str):
        start_time = datetime.now()
    
        # Create ephemeral dicts and queues
        with modal.Dict.ephemeral() as d, modal.Queue.ephemeral() as q:
            # The dict is used to signal the scraping to stop
            # The queue contains the URLs that have been crawled
    
            # Initialize queue with a starting URL
            q.put(url)
    
            # Crawl until the queue is empty, or reaching some number of URLs
            visited = set()
            max_urls = 50000
            while True:
                try:
                    next_urls = q.get_many(2000, timeout=5)
                except queue.Empty:
                    break
                new_urls = set(next_urls) - visited
                visited |= new_urls
                if len(visited) < max_urls:
                    crawl_pages.spawn(q, d, new_urls)
                else:
                    d["stop"] = True
    
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"Crawled {len(visited)} URLs in {elapsed:.2f} seconds")
    
    
    @app.local_entrypoint()
    def main():
        scrape.remote("https://www.wikipedia.org/")

Copy

Starting from Wikipedia, this spawns several dozen containers (auto-scaled on
demand) to crawl over 200,000 URLs in 40 seconds.

## Data durability

Dict and Queue objects are backed by an in-memory database, and thus are not
resilient to database server restarts. Queues and Dicts are also subject to
expiration, as described by the modal.Dict and modal.Queue reference pages.

Please get in touch if you need durability for Dict or Queue objects.

