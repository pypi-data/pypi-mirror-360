# Gethonis API

## About

A lightweight Python library to interact with the Gethonis API. Gethonis combines the best of OpenAI's ChatGPT responses with DeepSeek's capabilities for an enhanced conversational experience.


## Gethonis Class Arguments

### Basic Example

For messages

```python
import gethonis as geth

bot = geth.Gethonis("geth-...", "https://api.gethonis.com/")
message = "Test Meessage"
bot.set_message("gethonis", False)
print(bot.get_message(message))
```

For posts

```python
import gethonis as geth

bot = geth.Gethonis("geth-...", "https://api.gethonis.com/")
message = "Test Meessage"
bot.set_post("type")
print(bot.get_post(message))
```

**Models:**
* `gethonis`
* `openai`
* `deepseek`