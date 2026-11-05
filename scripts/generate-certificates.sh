#!/usr/bin/env bash
set -eu

# Generate a local root CA and a server certificate for controlled testing.
# The output directory may be changed by supplying a first argument.

output_dir="${1:-certificates}"
hostname="${2:-quothed.example.com}"

mkdir -p "$output_dir"
umask 077

openssl genrsa -out "$output_dir/root-ca.key" 4096
openssl req -x509 -new -nodes \
    -key "$output_dir/root-ca.key" \
    -sha256 -days 3650 \
    -out "$output_dir/root-ca.crt" \
    -subj "/C=XX/O=Quothed Learning/CN=Quothed Local Root CA"

openssl genrsa -out "$output_dir/server.key" 2048
openssl req -new \
    -key "$output_dir/server.key" \
    -out "$output_dir/server.csr" \
    -subj "/C=XX/O=Quothed Learning/CN=$hostname"

cat > "$output_dir/server.ext" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
subjectAltName=DNS:$hostname
EOF

openssl x509 -req \
    -in "$output_dir/server.csr" \
    -CA "$output_dir/root-ca.crt" \
    -CAkey "$output_dir/root-ca.key" \
    -CAcreateserial \
    -out "$output_dir/server.crt" \
    -days 825 -sha256 \
    -extfile "$output_dir/server.ext"

rm "$output_dir/server.csr" "$output_dir/server.ext" "$output_dir/root-ca.srl"

printf 'Generated certificates in %s\n' "$output_dir"
printf '  Root CA certificate: %s/root-ca.crt\n' "$output_dir"
printf '  Server certificate:  %s/server.crt\n' "$output_dir"
printf '  Server private key:  %s/server.key\n' "$output_dir"
