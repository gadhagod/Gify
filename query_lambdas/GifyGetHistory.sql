SELECT
    *
FROM
    "GifyHistory" g
WHERE
    g.user_id = :target_user_id
ORDER BY
    g._event_time DESC
LIMIT
    5