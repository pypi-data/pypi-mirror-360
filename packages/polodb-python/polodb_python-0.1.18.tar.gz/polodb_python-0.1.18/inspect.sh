for file in dist/*.tar.gz; do
  echo "Inspecting $file"
  gtar --wildcards -tzf "$file" | grep PKG-INFO || echo "PKG-INFO not found"
  gtar --wildcards -xOf "$file" */PKG-INFO || echo "Unable to read PKG-INFO"
done