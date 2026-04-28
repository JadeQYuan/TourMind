# dist/ 由构建脚本（build.sh / build.ps1）预编译，此处直接打包
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html
RUN mkdir -p /etc/nginx/ssl
EXPOSE 80 443
