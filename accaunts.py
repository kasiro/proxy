
# Чтобы добавить аккаунт — просто скопируй curl-команду сюда:


ACCOUNTS = [
    """
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; session=MTc5MDI3MTM3NXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQW9BQ0hWelpYSnVZVzFsQm5OMGNtbHVad3dVQUJKMVgyRXlOVGhtTm1ZM05qWTVNVE0zWVdNR2MzUnlhVzVuREFZQUJISnZiR1VEYVc1MEJBSUFBZ1p6ZEhKcGJtY01DQUFHYzNSaGRIVnpBMmx1ZEFRQ0FBSUdjM1J5YVc1bkRBY0FCV2R5YjNWd0JuTjBjbWx1Wnd3SkFBZGtaV1poZFd4MEJuTjBjbWx1Wnd3RUFBSnBaQU5wYm5RRUJBRC1ORFk9fMIRcO4-L69b0iXesHVLVkVZM8U3l6o63qSykHDrZVYk; OdiRouter-authenticated=1; _ym_isad=1' \
  -H 'new-api-user: 6683' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="153", "Not_A Brand";v="8"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: c1b131d1-d249-490a-aae6-904c95db4cf6' \
  -H 'x-starry-window-id: 8518f21c-9a81-4aa8-8884-57afc9f1a6f8' \
  --data-raw '{"group":"default","messages":[{"content":"привет?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'
""",
    """
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjM2MjIwN3xEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQWNBQldkeWIzVndCbk4wY21sdVp3d0pBQWRrWldaaGRXeDBCbk4wY21sdVp3d0VBQUpwWkFOcGJuUUVCQUQtT3RnR2MzUnlhVzVuREFvQUNIVnpaWEp1WVcxbEJuTjBjbWx1Wnd3VUFCSjFYek16TVRJM05qRTVZVEl5TkRNNFltVUdjM1J5YVc1bkRBWUFCSEp2YkdVRGFXNTBCQUlBQWdaemRISnBibWNNQ0FBR2MzUmhkSFZ6QTJsdWRBUUNBQUk9fFwYDmVJwzCT78ZfJtd6GvbGryz11pH2k5IQWyFOszz3; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7532' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="155", "Not(A:Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: df0302cb-055c-446b-aac4-28d41d2cb21c' \
  -H 'x-starry-window-id: e5b6d639-99da-431a-984a-1fa6a1fb679f' \
  --data-raw '{"group":"default","messages":[{"content":"hi","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjM2MjM2M3xEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA0ODZnWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmT1RRd1pqTTNOR05rWXpjMlpHUXhZd1p6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fM5aiWQtr8DMHGKqiUxLyhp62h-k6zHUXPnf8tLnLT5C; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7797' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="155", "Not(A:Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: df0302cb-055c-446b-aac4-28d41d2cb21c' \
  -H 'x-starry-window-id: e5b6d639-99da-431a-984a-1fa6a1fb679f' \
  --data-raw '{"group":"default","messages":[{"content":"hi","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjM2MjQ2M3xEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQWNBQldkeWIzVndCbk4wY21sdVp3d0pBQWRrWldaaGRXeDBCbk4wY21sdVp3d0VBQUpwWkFOcGJuUUVCQUQtUFBZR2MzUnlhVzVuREFvQUNIVnpaWEp1WVcxbEJuTjBjbWx1Wnd3VUFCSjFYMkprT0RKa1lXVm1Zak13TURZMFpUQUdjM1J5YVc1bkRBWUFCSEp2YkdVRGFXNTBCQUlBQWdaemRISnBibWNNQ0FBR2MzUmhkSFZ6QTJsdWRBUUNBQUk9fGVbo9pOK2NzsmnWbL4RjKq7A7FQh6FKNthyBpG2FUQa; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7803' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="155", "Not(A:Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: df0302cb-055c-446b-aac4-28d41d2cb21c' \
  -H 'x-starry-window-id: e5b6d639-99da-431a-984a-1fa6a1fb679f' \
  --data-raw '{"group":"default","messages":[{"content":"hi","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjM1ODcxMHxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA0OUJnWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmWVRNell6Z3dOMlZtWVdWa01XRmtNUVp6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fD2qYskAoFGCW1AZmL4hpz736PrpLFR78mE2RXDKSLEU; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7811' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="155", "Not(A:Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: d9e26b2c-3d1b-4cd6-ad40-e11b87e90f96' \
  -H 'x-starry-window-id: e71126a8-a8c4-439b-9291-45de35aeef31' \
  --data-raw '{"group":"default","messages":[{"content":"привет?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjA4NTg2MXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQWdBQm5OMFlYUjFjd05wYm5RRUFnQUNCbk4wY21sdVp3d0hBQVZuY205MWNBWnpkSEpwYm1jTUNRQUhaR1ZtWVhWc2RBWnpkSEpwYm1jTUJBQUNhV1FEYVc1MEJBUUFfajBJQm5OMGNtbHVad3dLQUFoMWMyVnlibUZ0WlFaemRISnBibWNNRkFBU2RWOHlZams1TnpJMU1tWTBaakl6TWpWaUJuTjBjbWx1Wnd3R0FBUnliMnhsQTJsdWRBUUNBQUk9fGdz4yeBstyAwTGK5setrOnP__QvEv5DBjIGVi434Psj; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7812' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="153", "Not_A Brand";v="8"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: c1b131d1-d249-490a-aae6-904c95db4cf6' \
  -H 'x-starry-window-id: 8518f21c-9a81-4aa8-8884-57afc9f1a6f8' \
  --data-raw '{"group":"default","messages":[{"content":"привет?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjA4NTc2MnxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA0OUNnWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmWVdWbE9UazVOVGhqTldZNE4yRXhNZ1p6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fJ9pucy6gxDY6Tm2Fr7c1AzyQS-tlnQPXKxFuaJ8XjtV; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7813' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="153", "Not_A Brand";v="8"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: c1b131d1-d249-490a-aae6-904c95db4cf6' \
  -H 'x-starry-window-id: 8518f21c-9a81-4aa8-8884-57afc9f1a6f8' \
  --data-raw '{"group":"default","messages":[{"content":"привет?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjA4NjMxM3xEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA1RW5nWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmTmpaaE1qUTRNelUwTUdWbFpERXhOUVp6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fN40iLuTu-JBQsxhbFlvwG2ED4BAubg6RpdYErRL0pzr; OdiRouter-authenticated=1' \
  -H 'new-api-user: 8783' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="153", "Not_A Brand";v="8"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: c1b131d1-d249-490a-aae6-904c95db4cf6' \
  -H 'x-starry-window-id: 8518f21c-9a81-4aa8-8884-57afc9f1a6f8' \
  --data-raw '{"group":"default","messages":[{"content":"привет?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjA4NjIxOXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQW9BQ0hWelpYSnVZVzFsQm5OMGNtbHVad3dVQUJKMVh6QTNZV1l6TURVelpqUmtZV0kyTldJR2MzUnlhVzVuREFZQUJISnZiR1VEYVc1MEJBSUFBZ1p6ZEhKcGJtY01DQUFHYzNSaGRIVnpBMmx1ZEFRQ0FBSUdjM1J5YVc1bkRBY0FCV2R5YjNWd0JuTjBjbWx1Wnd3SkFBZGtaV1poZFd4MEJuTjBjbWx1Wnd3RUFBSnBaQU5wYm5RRUJBRC1SS0k9fASK4NXsyZEiC4Hkulq8LTIfAmCl1upZvEWXXB81KqqL; OdiRouter-authenticated=1' \
  -H 'new-api-user: 8785' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="153", "Not_A Brand";v="8"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: c1b131d1-d249-490a-aae6-904c95db4cf6' \
  -H 'x-starry-window-id: 8518f21c-9a81-4aa8-8884-57afc9f1a6f8' \
  --data-raw '{"group":"default","messages":[{"content":"привет?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
]
