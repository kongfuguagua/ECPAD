FROM busybox:stable-musl
WORKDIR /bin
ADD . .
RUN chmod 777  tonodename
CMD ["tonodename","--v=3","--config=/etc/kubernetes/scheduler-config.yaml"]