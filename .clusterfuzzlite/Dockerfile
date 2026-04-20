FROM gcr.io/oss-fuzz-base/base-builder-python@sha256:c623f1432467c90f8186aa504d402ea4960bd3dd7475579448bdb7620d6c4d77
COPY . $SRC/snowflake-cortex-translate
WORKDIR $SRC/snowflake-cortex-translate
COPY .clusterfuzzlite/build.sh $SRC/
