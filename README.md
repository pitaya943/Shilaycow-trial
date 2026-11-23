# Shilaycow-trial

A small todo API. To run it:

```
pip install -r requirements.txt
python -m uvicorn todo_api.app:create_app --factory --host 127.0.0.1 --port 8765
```

A todo can be given a priority when it is created: `low`, `normal` or `high`. Without one it is `normal`. Any other value (including `High`, `" high"` or `""`) is refused with 422 and nothing is added. Every todo the API returns carries its `priority`:

```
curl -X POST localhost:8765/todos -H 'content-type: application/json' -d '{"title": "繳房租", "priority": "high"}'
```

A title is at most 200 characters once surrounding whitespace is trimmed; a longer one is refused with 422 (`title must be at most 200 characters`) and nothing is added.

The todos are kept in `todos.db` in the directory the service is started from; set `TODO_DB` to keep them somewhere else. They are still there after a restart.

If that file exists but is not this service's data (something else wrote it, or it is damaged), the service refuses to start, names the file, and leaves it untouched.
