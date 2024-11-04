#!/bin/bash

# Set default variables
JAVA_HOME="/usr/lib/jvm/java-11-openjdk"  
INDEXING_DIR="../indexing/inverted_index"  
OUTPUT_DIR="../output/index"  
LOG_FILE="index_build.log"

# Check if the required directories exist
if [ ! -d "$INDEXING_DIR" ]; then
  echo "Indexing directory does not exist: $INDEXING_DIR"
  exit 1
fi

# Create output directory if it does not exist
mkdir -p $OUTPUT_DIR

# Build the index using Java
echo "Starting index build process..."
cd $INDEXING_DIR

# Compile Java files
$JAVA_HOME/bin/javac -d $OUTPUT_DIR *.java
if [ $? -ne 0 ]; then
  echo "Compilation failed, check logs for details."
  exit 1
fi

# Run the index builder
$JAVA_HOME/bin/java -cp $OUTPUT_DIR inverted_index_builder
if [ $? -ne 0 ]; then
  echo "Index building failed, check logs for details." | tee -a $LOG_FILE
  exit 1
fi

# Success message
echo "Index built successfully! Output stored in $OUTPUT_DIR"

exit 0