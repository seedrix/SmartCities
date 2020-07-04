# Shops
## /shops/all
### get
returns a list of all shops

## /shops/shop/{string:shop_id}
### get
return: requested shop
### put
create shop with associated shop_id

example body:
```
{
    "max_people1" : 2,
    "sensors" : [ 
        "bB8:27:EB:2A:C9:E6", 
        "wb8:27:eb:d5:36:19", 
        "ccamera0"
    ],
    "shop_name" : "BLF - Best Local Food",
    "logo" : "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiID8+CTwhLS0gR2VuZXJhdG9yOiBBc3NlbWJseSAyLjIgLSBodHRwOi8vYXNzZW1ibHlhcHAuY28gLS0+CTxzdmcgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB3aWR0aD0iMjA0OC4wMCIgaGVpZ2h0PSIyMDQ4LjAwIiB2aWV3Qm94PSIwIDAgMjA0OC4wIDIwNDguMCI+CQk8ZyBpZD0iZG9jdW1lbnQiIHRyYW5zZm9ybT0ibWF0cml4KDEsMCwwLDEsMTAyNC4wLDEwMjQuMCkiPgkJCTxwYXRoIGQ9Ik0tMzg5Ljk0NCwtMzQyLjY4OCBDLTQ5Ny44NzIsLTE5Mi4zODMgLTQ5NC42MjQsNDUuNDc5MyAtMzg0LjM2LDE3Ny43ODggQy0yMzEuMjE1LDM1OS4yNzUgNDYuODQ0MywzNjEuNzgxIDIyOC45MzEsMTk0LjMwNyBDMjQ4LjU1NiwxNzYuMTQzIDI3NC40MDEsMTQyLjk0MSAzMDUuMDIxLDE3Ny43ODggQzMzNS42NDEsMjEyLjYzNCAyMTcuMjUxLDI5Ny4yMjMgMTQ2LjcwMiwzMjcuODMyIEM3Ni4xNTI3LDM1OC40NDEgMTcuMTc0NCwzNjYuMDg4IC0zOC45NDk5LDM2OS45NTcgQy05NS4wNzQxLDM3My44MjcgLTE0OC4xOTIsMzU0LjQ1NSAtMTc3LjM2NywzNDQuMTc1IEMtMTg0LjExMywzNDIuMTUzIC0xODkuNzM3LDM1MC43IC0xODQuNjIyLDM1NS44MTUgQzU2LjI1MTMsNDkxLjgxNSAxODQuNzM5LDQ0Mi43MSAzODEuNjE4LDMxMy45MjggQzQyMS42ODQsMjg3LjcyIDQyMS40NDcsMjIxLjQ5MiAzODIuNzI0LDE4Mi43NjggTDMwNS4wMjEsMTA1LjA2NiBMMjY5LjIyLDY5LjI2NDMgTC0xMjguMjQ4LC0zMjguMjAzIEwtMjE0LjQ2MywtNDE0LjQxOSBDLTI0NS4xNSwtNDQ1LjEwNiAtMjk2LjcwMywtNDQ0LjY5NyAtMzMwLjUsLTQxMi4zNjEgQy0zNTIuNjAxLC0zODguNzk5IC0zNzIuMzQsLTM2Ny41OTkgLTM4OS45NDQsLTM0Mi42ODggWiBNLTI4NS4zMjEsLTMwMS42MTcgTC0zNDIuNjExLC0zMDEuNjE3IEwtMjg1LjMyMSwtMzQ5LjY4NiBMLTI4NS4zMjEsLTMwMS42MTcgWiBNLTMuMzQyNTNlLTA2LDgzLjk2NyBMLTU3LjI5MDEsODMuOTY3IEw1LjY4NDM0ZS0xNCwzNS44OTc2IEwtMy4zNDI1M2UtMDYsODMuOTY3IFogTS0yODUuMzIxLDU5LjkzMjMgTC0zNDIuNjExLDU5LjkzMjMgTC0yODUuMzIxLDExLjg2MjkgTC0yODUuMzIxLDU5LjkzMjMgWiBNLTExMy4xOTUsMjUzLjIyIEwtMTcwLjQ4NiwyNTMuMjIgTC0xMTMuMTk1LDIwNS4xNTEgTC0xMTMuMTk1LDI1My4yMiBaIE0zMzYuODExLDMwMS4yOSBMMjc5LjUyMSwzMDEuMjkgTDMzNi44MTEsMjUzLjIyIEwzMzYuODExLDMwMS4yOSBaICIgZmlsbD0iIzAwMDAwMCIgZmlsbC1vcGFjaXR5PSIxLjAwIiAvPgkJPC9nPgk8L3N2Zz4="
}
```

## /shops/people/{string:shop_id}
#### get 
return: current number of people at the requested shop

## /shops/people/{string:shop_id}/{int:timestamp}
### get
return: all people data for the given shop after the requested timestamp

# User
## /user/next_shop
### get
requirement: bearer token

return: user's next shop

## /user/shops
### get
requirement: bearer token

return: user's shop list

### post
requirement: bearer token

set the user's shop list

example body:
```
[
  "shop1",
  "shop2"
]
```

## /user/shops/{string:shop_id}
### delete
deletes the requested shop from the user's shop list

# Auth
## /auth/signup
### post
register a new user

example body:
```
{
	"email" : "test@gmail.com",
	"password" : "test1234"
}
```

## /auth/login
log in a registered user

example body:
```
{
	"email" : "test@gmail.com",
	"password" : "test1234"
}
```
returns: bearer token