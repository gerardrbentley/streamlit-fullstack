FROM golang:1.17-alpine3.15 as builder
COPY go.mod go.sum /go/src/fullstack/backend/
WORKDIR /go/src/fullstack/backend
RUN go mod download
COPY . /go/src/fullstack/backend
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o build/app fullstack/backend

FROM alpine
RUN apk add --no-cache ca-certificates && update-ca-certificates
COPY --from=builder /go/src/fullstack/backend/build/app /usr/bin/app
ENTRYPOINT ["/usr/bin/app"]