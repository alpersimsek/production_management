FROM ghcr.io/cirruslabs/flutter:stable AS build-env

WORKDIR /app

COPY pubspec.yaml pubspec.lock ./

RUN flutter pub get

COPY . .

# Enable web support
RUN flutter config --enable-web

RUN flutter build web --release --web-renderer html

# fix assets path
RUN mv /app/build/web/assets/assets/* /app/build/web/assets/
RUN rm -rf /app/build/web/assets/assets

# Stage 2 - Create the run-time image
FROM nginx:stable-alpine
COPY web/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build-env /app/build/web /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# CMD ["flutter", "run", "-d", "web-server", "--web-hostname", "0.0.0.0", "--web-port", "80"]