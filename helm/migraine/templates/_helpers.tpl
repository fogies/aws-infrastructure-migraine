{{- define "secretImagePullEncoded" -}}
{{- with .Values -}}
{{- (printf "{\"auths\":{\"%s\":{\"username\":\"%s\",\"password\":\"%s\",\"auth\":\"%s\"}}}" .registryUrl .registryUser .registryPassword (printf "%s:%s" .registryUser .registryPassword | b64enc)) | b64enc -}}
{{- end -}}
{{- end -}}
