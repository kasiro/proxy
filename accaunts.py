
# Чтобы добавить аккаунт — просто скопируй curl-команду сюда:
ACCOUNTS = [
    """
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -b 'odirouter_attribution=eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9; session=MTc4NzU5NjE5OHxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA0ME5nWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmWVRJMU9HWTJaamMyTmpreE16ZGhZd1p6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fFIuzeMj0iVgJarefB1qWCLBaPYEOZ906ON_FTcOUS9R; OdiRouter-authenticated=1' \
  -H 'new-api-user: 6683' \
  -H 'origin: https://odirouter.ai' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Not=A?Brand";v="99", "Brave";v="151", "Chromium";v="151"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-gpc: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36' \
  -H 'x-odirouter-attribution: eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 8da9eb87-50f7-4718-b05d-f1cdd47d8556' \
  -H 'x-starry-ref-page-id: usage_page' \
  -H 'x-starry-ref-page-name: usage_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/usage' \
  -H 'x-starry-session-id: 54c5dd74-6a1e-4a8c-af99-0d74034d23fe' \
  -H 'x-starry-window-id: ae3f565b-d658-4070-a04e-78060cc876d3' \
  --data-raw '{"group":"default","messages":[{"content":"ну что? поиграем в угадайку?","role":"user"}],"model":"free-claude-haiku-4.5","stream":true}'
""",
    """
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -b 'odirouter_attribution=eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9; session=MTc4ODE4NzQ5N3xEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA0NjJBWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmTXpNeE1qYzJNVGxoTWpJME16aGlaUVp6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fCGCjD1piXmXI-h4QJMHOQ5eQznQMcWNDtJsSmO3R2l6; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7532' \
  -H 'origin: https://odirouter.ai' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Not=A?Brand";v="99", "Brave";v="151", "Chromium";v="151"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-gpc: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36' \
  -H 'x-odirouter-attribution: eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 8da9eb87-50f7-4718-b05d-f1cdd47d8556' \
  -H 'x-starry-ref-page-id: model_page' \
  -H 'x-starry-ref-page-name: model_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/models' \
  -H 'x-starry-session-id: dff70769-1759-426f-aa32-9d80d0d8a6bb' \
  -H 'x-starry-window-id: 5fcce5c8-4879-4e6b-9f7a-0deb796a0619' \
  --data-raw '{"group":"default","messages":[{"content":"привет","role":"user"}],"model":"free-minimax-m2.7","stream":true}'
""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -b 'odirouter_attribution=eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9; session=MTc4ODQ0MjE3NXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA0ODZnWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmT1RRd1pqTTNOR05rWXpjMlpHUXhZd1p6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fG-fxgPZk03tDXjJMPf5NWK51VUV0C9LTC3Hc1KHi4yz; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7797' \
  -H 'origin: https://odirouter.ai' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Not=A?Brand";v="99", "Brave";v="151", "Chromium";v="151"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-gpc: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36' \
  -H 'x-odirouter-attribution: eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 8da9eb87-50f7-4718-b05d-f1cdd47d8556' \
  -H 'x-starry-ref-page-id: usage_page' \
  -H 'x-starry-ref-page-name: usage_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/usage' \
  -H 'x-starry-session-id: 92a098c3-a205-491b-907e-c5d1c1ef4914' \
  -H 'x-starry-window-id: 87505ed9-91e7-4d49-9ff1-b4ffbfaa6f3c' \
  --data-raw $'{"group":"default","messages":[{"content":"привет\u0021","role":"user"}],"model":"free-minimax-m2.7","stream":true}'
""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -b 'odirouter_attribution=eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9; session=MTc4ODQ0NDY1MHxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQW9BQ0hWelpYSnVZVzFsQm5OMGNtbHVad3dVQUJKMVgySmtPREprWVdWbVlqTXdNRFkwWlRBR2MzUnlhVzVuREFZQUJISnZiR1VEYVc1MEJBSUFBZ1p6ZEhKcGJtY01DQUFHYzNSaGRIVnpBMmx1ZEFRQ0FBSUdjM1J5YVc1bkRBY0FCV2R5YjNWd0JuTjBjbWx1Wnd3SkFBZGtaV1poZFd4MEJuTjBjbWx1Wnd3RUFBSnBaQU5wYm5RRUJBRC1QUFk9fKpYGB-O335XebpiahfLdBKJbh_4D-xLa5uNXsdSW2uP; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7803' \
  -H 'origin: https://odirouter.ai' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Not=A?Brand";v="99", "Brave";v="151", "Chromium";v="151"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-gpc: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36' \
  -H 'x-odirouter-attribution: eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 8da9eb87-50f7-4718-b05d-f1cdd47d8556' \
  -H 'x-starry-ref-page-id: apikey_page' \
  -H 'x-starry-ref-page-name: apikey_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/api-keys' \
  -H 'x-starry-session-id: bdc1faca-4fd1-488c-813a-131f4193168c' \
  -H 'x-starry-window-id: d8746b50-7206-44d3-9beb-c7e9a4b9eb34' \
  --data-raw $'{"group":"default","messages":[{"content":"Привет","role":"user"},{"content":"Привет\u0021 👋\\n\\nРад видеть тебя\u0021 Как я могу помочь тебе сегодня?","role":"assistant"},{"content":"как у тебя дела?","role":"user"}],"model":"free-minimax-m2.7","stream":true}'
""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -b 'odirouter_attribution=eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9; session=MTc4ODQ0ODY0MXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA0OUJnWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmWVRNell6Z3dOMlZtWVdWa01XRmtNUVp6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fMUzWcfNwGrtkvfaKfFBo2_5MZmdvypYkfuybgZeqP9c; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7811' \
  -H 'origin: https://odirouter.ai' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Not=A?Brand";v="99", "Brave";v="151", "Chromium";v="151"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-gpc: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36' \
  -H 'x-odirouter-attribution: eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 8da9eb87-50f7-4718-b05d-f1cdd47d8556' \
  -H 'x-starry-ref-page-id: model_page' \
  -H 'x-starry-ref-page-name: model_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/models' \
  -H 'x-starry-session-id: 514207b2-f19c-47ec-a5b0-49cab3fd32bf' \
  -H 'x-starry-window-id: f135f574-2da9-41b5-816f-65c2c520ebb6' \
  --data-raw $'{"group":"default","messages":[{"content":"Привет\u0021 что ты умеешь?","role":"user"}],"model":"free-minimax-m2.7","stream":true}'
""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -b 'odirouter_attribution=eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9; session=MTc4ODQ0OTAxNXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA0OUNBWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmTW1JNU9UY3lOVEptTkdZeU16STFZZ1p6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fOJNnwjx6CA68hdKSl8OtC8f2z3iMTkclzoOVNmkywHk; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7812' \
  -H 'origin: https://odirouter.ai' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Not=A?Brand";v="99", "Brave";v="151", "Chromium";v="151"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-gpc: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36' \
  -H 'x-odirouter-attribution: eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 8da9eb87-50f7-4718-b05d-f1cdd47d8556' \
  -H 'x-starry-ref-page-id: model_page' \
  -H 'x-starry-ref-page-name: model_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/models' \
  -H 'x-starry-session-id: 514207b2-f19c-47ec-a5b0-49cab3fd32bf' \
  -H 'x-starry-window-id: f135f574-2da9-41b5-816f-65c2c520ebb6' \
  --data-raw '{"group":"default","messages":[{"content":"Привет? что ты умеешь? какого ты года рождения?","role":"user"}],"model":"free-minimax-m2.7","stream":true}'
""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -b 'odirouter_attribution=eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9; session=MTc4ODQ0OTI1M3xEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQWdBQm5OMFlYUjFjd05wYm5RRUFnQUNCbk4wY21sdVp3d0hBQVZuY205MWNBWnpkSEpwYm1jTUNRQUhaR1ZtWVhWc2RBWnpkSEpwYm1jTUJBQUNhV1FEYVc1MEJBUUFfajBLQm5OMGNtbHVad3dLQUFoMWMyVnlibUZ0WlFaemRISnBibWNNRkFBU2RWOWhaV1U1T1RrMU9HTTFaamczWVRFeUJuTjBjbWx1Wnd3R0FBUnliMnhsQTJsdWRBUUNBQUk9fIq0iYeEBHI53dU-6r_MBEK3tFWN4BelsUkbYOaiazzj; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7813' \
  -H 'origin: https://odirouter.ai' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Not=A?Brand";v="99", "Brave";v="151", "Chromium";v="151"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-gpc: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36' \
  -H 'x-odirouter-attribution: eyJjYXB0dXJlZF9hdCI6MTc4NzU5NTkyNiwiZXhwaXJlc19hdCI6MTc5MDE4NzkyNiwibGFuZGluZ19wYXRoIjoiL29wZW5yb3V0ZXIiLCJwcm9wZXJ0aWVzIjp7InV0bV9zb3VyY2UiOiJ5YSIsImFkIjoiUlVZRFhPREZDMDI0In0sInJ1bGVfaWQiOjQ4LCJyb3V0ZV9uYW1lIjoib3BlbnJvdXRlciJ9' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 8da9eb87-50f7-4718-b05d-f1cdd47d8556' \
  -H 'x-starry-ref-page-id: credits_page' \
  -H 'x-starry-ref-page-name: credits_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/credits' \
  -H 'x-starry-session-id: 514207b2-f19c-47ec-a5b0-49cab3fd32bf' \
  -H 'x-starry-window-id: f135f574-2da9-41b5-816f-65c2c520ebb6' \
  --data-raw '{"group":"default","messages":[{"content":"Привет?","role":"user"}],"model":"free-minimax-m2.7","stream":true}'
""",
]
