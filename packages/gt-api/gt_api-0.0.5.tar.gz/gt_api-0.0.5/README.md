# geotastic-api

## Installation

```
python3 -m pip install gt_api
```
(also installs requirements)

## Usage

### Logging in

Most API requests require logging in. There are two ways to do it: 

1. mail + password
1. token

#### Mail + Password

```python
import gt_api
client=gt_api.Client.login('your.mail@example.com', 'hunter2')
```

And you're in! The big caveat is that this logs you out of any other sessions, and also causes API costs.
So for most use cases you want to use tokens.

#### Token

```python
import gt_api
client=gt_api.Client('d8f350a3f557adc253f5003a81d3098c06dea93f84edf10e3fabc1d92acd1771')
```

##### How do I get it?

Go to geotastic and log in with your account.
Then open the developer tools (F12 or ctrl-shift-i). Then navigate to Storage(Application-&gt;Storage for Chrome)-&gt;Local Storage-&gt;https://geotastic.net/ and scroll down to *token*. Copy the value.

Please note that the token is one per session, so once you log out of the session you got the token from, you'll need to update it.
#### Without Login

Use `Client(None)`.
Most functions will not work.
#### Accessing user data
```python
data = client.user_data
nickname = data['nickname']
uid = data['uid']
```
### Creating a drop group

```python
map_id=12345
group = client.create_drop_group(map_id, -12.345, -69.420, 'pe', 'My Drop Group', active=True, bias=5.3)
print(group["dropGroup"]["id"])
```

### Listing drop groups

```python
client.get_drop_groups(12345)
```
If you don't own the map, use `get_public_drop_groups()`

### Exporting drops

```python
client.get_map_drops(12345)
```
or
```python
client.get_group_drops(12345)
```
You DON'T need to own the map or the group.

### Importing drops

```python
drops=[{"id":1,"style":"streetview","lat":39.28719501248246,"lng":-103.07696260471509,"code":"us","panoId":"Ple0qA2-cNzxc0K-gXgbFA"}]
client.import_drops(drops, 12345, target_type="map", import_type="merge")
```

Possible target types are `map` and `group`.
Possible import types are `merge`, `override` and `update`.

### Lobbies

Lobbies are handled a little differently.
To create a lobby, use `Lobby.create(token)`.
To join a lobby, user `Lobby.join(token, lobby_id)`.
You then add handlers for events coming in from the Lobby socket using the `lobby.add_handler("event")` decorator. The handler for the event "\*" will be called for every event.
You can send socket messages to the lobby using `lobby.send_message(type, **kwargs)`. The kwargs will be added to the message json.
You can make lobby api requests using `lobby.lobby_api_request(url, method *args, **kwargs)`. Args and kwargs will be passed to `request.request()`.
To run the lobby event loop, use `Lobby.run()`
To disconnect from the lobby, use `Lobby.disconnect()`
Look at `examples/auto_lobby.py`
### Other uses

There's loads more I can't be bothered to document. Check the source code.


## Contributing

If you'd like to have a feature that's not in the library, just create a github issue and I'll get to it (maybe).

If you'd like to add your own, it's pretty easy. Just use developer tools to check which api calls geotastic is making and then remake them as functions. If the calls are encrypted, use `gt_api.generic.decode_encdata`.


