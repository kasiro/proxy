
# Чтобы добавить аккаунт — просто скопируй curl-команду сюда:


ACCOUNTS = [
    """
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; mdd=0; session=MTc5Mjk0MTEyNnxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVlBQkhKdmJHVURhVzUwQkFJQUFnWnpkSEpwYm1jTUNBQUdjM1JoZEhWekEybHVkQVFDQUFJR2MzUnlhVzVuREFjQUJXZHliM1Z3Qm5OMGNtbHVad3dKQUFka1pXWmhkV3gwQm5OMGNtbHVad3dFQUFKcFpBTnBiblFFQkFELU5EWUdjM1J5YVc1bkRBb0FDSFZ6WlhKdVlXMWxCbk4wY21sdVp3d1VBQkoxWDJFeU5UaG1ObVkzTmpZNU1UTTNZV009fOce4Hw6auW-YpaPk5UNEZEUSLeZGLCzszhgY7H16Szt; OdiRouter-authenticated=1' \
  -H 'new-api-user: 6683' \
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
  -H 'x-starry-session-id: 61d039a0-f414-4444-b719-28a8178c90b6' \
  -H 'x-starry-window-id: 7bdede60-396d-4b52-9448-b0ccd8a8abd0' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'
""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b '_ym_uid=1790271334319132896; _ym_d=1794312443; _ym_isad=1; mdd=0; session=MTc5NDc4Nzk1OXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQWNBQldkeWIzVndCbk4wY21sdVp3d0pBQWRrWldaaGRXeDBCbk4wY21sdVp3d0VBQUpwWkFOcGJuUUVCQUQtWFVnR2MzUnlhVzVuREFvQUNIVnpaWEp1WVcxbEJuTjBjbWx1Wnd3VUFCSjFYMlkwTWpJNU5EazRaVGt4WWpjNE1EUUdjM1J5YVc1bkRBWUFCSEp2YkdVRGFXNTBCQUlBQWdaemRISnBibWNNQ0FBR2MzUmhkSFZ6QTJsdWRBUUNBQUk9fLJVmk8gUiGPhJS-UBOP-3JmG88FQa3_JDZ5TNb3dzg3; OdiRouter-authenticated=1' \
  -H 'new-api-user: 11940' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="157", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: model_page' \
  -H 'x-starry-ref-page-name: model_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/models' \
  -H 'x-starry-session-id: 9d876b80-bdd2-406f-a278-be52a9ae5842' \
  -H 'x-starry-window-id: 95351ac7-aaa9-4873-a223-1129660e533a' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'
""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b '_ym_uid=1790271334319132896; _ym_d=1794312443; _ym_isad=1; mdd=0; session=MTc5NDc4ODA4OXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA1ZFNnWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmTURCallqQmtNekl5WmpKaU9EaGtPUVp6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fAtPOJ9xl_pPvqfLwTPrV3oQwaybSq3wJiT_xB37wDrT; OdiRouter-authenticated=1' \
  -H 'new-api-user: 11941' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="157", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: model_page' \
  -H 'x-starry-ref-page-name: model_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/models' \
  -H 'x-starry-session-id: 9d876b80-bdd2-406f-a278-be52a9ae5842' \
  -H 'x-starry-window-id: 95351ac7-aaa9-4873-a223-1129660e533a' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-gemini-3-flash-preview","stream":true}'
""",
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
  -b '_ym_uid=1790271334319132896; _ym_d=1794312443; _ym_isad=1; mdd=0; session=MTc5NDc4NzY3NHxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQW9BQ0hWelpYSnVZVzFsQm5OMGNtbHVad3dVQUJKMVgyRmxaVGs1T1RVNFl6Vm1PRGRoTVRJR2MzUnlhVzVuREFZQUJISnZiR1VEYVc1MEJBSUFBZ1p6ZEhKcGJtY01DQUFHYzNSaGRIVnpBMmx1ZEFRQ0FBSUdjM1J5YVc1bkRBY0FCV2R5YjNWd0JuTjBjbWx1Wnd3SkFBZGtaV1poZFd4MEJuTjBjbWx1Wnd3RUFBSnBaQU5wYm5RRUJBRC1QUW89fAoPaLmJ3LI4u4S9TDXF5huhCrKG_bJ6RJcP4WHIAEoZ; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7813' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="157", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: 9d876b80-bdd2-406f-a278-be52a9ae5842' \
  -H 'x-starry-window-id: 95351ac7-aaa9-4873-a223-1129660e533a' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
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
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b '_ym_uid=1790271334319132896; _ym_d=1794312443; _ym_isad=1; mdd=0; session=MTc5NDc4NzU4NHxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA1WmxBWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmWm1FM05UVTNObVUxWlRabE1qY3hZUVp6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fCSlPZ3yXtaUJCCeLW74JwzUYOfXjgzhhaXVQlZ_HJfL; OdiRouter-authenticated=1' \
  -H 'new-api-user: 11466' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="157", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: 9d876b80-bdd2-406f-a278-be52a9ae5842' \
  -H 'x-starry-window-id: 95351ac7-aaa9-4873-a223-1129660e533a' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b '_ym_uid=1790271334319132896; _ym_d=1794312443; _ym_isad=1; mdd=0; session=MTc5NDc4NzQ1NHxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQWdBQm5OMFlYUjFjd05wYm5RRUFnQUNCbk4wY21sdVp3d0hBQVZuY205MWNBWnpkSEpwYm1jTUNRQUhaR1ZtWVhWc2RBWnpkSEpwYm1jTUJBQUNhV1FEYVc1MEJBUUFfbG1XQm5OMGNtbHVad3dLQUFoMWMyVnlibUZ0WlFaemRISnBibWNNRkFBU2RWODNZVFkwTW1Jek4yUmtOVGszWmpka0JuTjBjbWx1Wnd3R0FBUnliMnhsQTJsdWRBUUNBQUk9fONAgBPBs_y_PsfXG1JZxJD1NQLPbkYDyc95vK8-dsqR; OdiRouter-authenticated=1' \
  -H 'new-api-user: 11467' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="157", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: 9d876b80-bdd2-406f-a278-be52a9ae5842' \
  -H 'x-starry-window-id: 95351ac7-aaa9-4873-a223-1129660e533a' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
]
