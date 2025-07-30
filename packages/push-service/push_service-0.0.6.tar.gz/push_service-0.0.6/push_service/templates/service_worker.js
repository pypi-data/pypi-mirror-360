self.addEventListener('notificationclick', function (event) {
    event.notification.close();
    if (event.notification.data && event.notification.data.action) {
        event.waitUntil(
            clients.openWindow(event.notification.data.action)
        );
    }
});

self.addEventListener('push', function (event) {
    let title, options;
    try {
        let data = event.data.json();
        title = data.title?data.title:'Notification';
        options = {
            body:  data.body,
            icon: data.icon,
            image: data.image,
            data : {action : data.action?data.action:'${server_address}/channel/${channel}'},
            silent: data.silent,
            renotify: true,
            tag: '${channel}',
        };
    } catch (error) {
        title = event.data ? event.data.text() : 'Notification';
        options = {
            data : {action : '${server_address}/${channel}'}
        };
    }
    const promiseChain = self.registration.showNotification(title, options);

    event.waitUntil(promiseChain);
});
