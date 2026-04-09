SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE();

SELECT AI_TRANSLATE('Hello world', 'en', 'ko', TRUE) AS translation_payload;

SELECT AI_TRANSLATE('Voy a likear tus fotos en Insta.', '', 'en', TRUE) AS translation_payload;

CREATE OR REPLACE TEMP TABLE demo_translation_input (
  id INT,
  source_text STRING,
  source_language STRING,
  target_language STRING
);

INSERT INTO demo_translation_input (id, source_text, source_language, target_language)
VALUES
  (1, 'Good morning', 'en', 'de'),
  (2, '¿Dónde está la estación?', 'es', 'en');

WITH translated AS (
  SELECT
    id,
    AI_TRANSLATE(source_text, source_language, target_language, TRUE) AS translation_payload
  FROM demo_translation_input
)
SELECT
  id,
  translation_payload:value::STRING AS translated_text,
  translation_payload:error::STRING AS translation_error
FROM translated
ORDER BY id;
