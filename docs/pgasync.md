# Async Data Flow

To avoid some performance issues, all communication with the database
is async using the *asyncpg* module. If using the async model in
SQLAlchemy, it uses asyncpg as well. Performance wise, depending on
the actual operation, asyncpg may be faster than *psycopg2* or not.

# Initialization

When using asyncpg, the *__init()__* method in a class cannot have any
calls to an async routine. This is because it's a constructor. This
then requires two steps to initialize a class. The first one
constructs an instantiation of the class, the following line then
calls **connect**, whichfrom then on is fully async.

## Defining methods

Each class must have *async* in front of the *def* if it is to call
any async code. Since this gets messy really fast, I just make all the
defs async to avoid confusion. For example:

    async def importDB(self, table: str, ):

## Calling A Method

To call any async method, you need to prefix it with *await*. I think
of it this way, *async def* puts the task on a list, and await pulls
it out. Nice and simple. For example:

	data = await self.tmdb.execute(sql)

# Threading

Originally this propject was using *concurrent.futures* for threading,
but has switched entirely to the *asynio* module using asychronis
tasks instead of threads since everything is designed to work
together.

All the code is heavily threaded. Data is split into chunks based on
the number of CPU cores. Then each chunk is then handed off to an async
Task to process the data. Since the threading is buried deep in this API,
it shouldn't be needed in most applications using the TM-Admin API will
need to do threading at a higher level for any of the data flow.
