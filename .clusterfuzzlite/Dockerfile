FROM gcr.io/oss-fuzz-base/base-builder-python@sha256:aeff3d6f9b3cb7aeb35982e75333188a22c2f225b4084cacff612da9f48e2761@sha256:aeff3d6f9b3cb7aeb35982e75333188a22c2f225b4084cacff612da9f48e2761
COPY . $SRC/snowflake-cortex-translate
WORKDIR $SRC/snowflake-cortex-translate
COPY .clusterfuzzlite/build.sh $SRC/
