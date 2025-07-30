from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def addition(a, b):
    """Add two numbers"""
    a = int(a)
    b = int(b)
    print(f"Adding {a} and {b} answer by Harshil")
    return a + b

@mcp.tool()
def multiply(a, b):
    """Multiply two numbers"""
    a = int(a)
    b = int(b)
    print(f"Multiplying {a} and {b} answer by Harshil")
    return a * b

def main():
    mcp.run(transport='stdio')

if __name__ == '__main__':
    main()