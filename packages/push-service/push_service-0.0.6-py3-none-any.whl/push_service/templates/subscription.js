'use strict';

const pushButton = document.getElementById("enablePush");

let isSubscribed = false;
let swRegistration = null;

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function updateSubscriptionOnServer(subscription,action) {
  if (subscription) {
    fetch('${channel}/'+action, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(subscription),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to send subscription to the server');
      }
    })
    .catch(error => {
      console.error('Error sending subscription to server: ', error);
    });
  }
}

function subscribeUser() {
  swRegistration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlB64ToUint8Array("${vapid_public_key}")
  })
  .then(function(subscription) {
    updateSubscriptionOnServer(subscription,'subscribe');
    isSubscribed = true;
    updateBtn();
  })
  .catch(function(error) {
    console.log('Error subscribing', error);
  });
}

function unsubscribeUser() {
  let subscription_info = null;
  swRegistration.pushManager.getSubscription()
  .then(function(subscription) {
    if (subscription) {
      subscription_info = subscription;
      return subscription.unsubscribe();
    }
  })
  .then(function() {
    updateSubscriptionOnServer(subscription_info,'unsubscribe');
    isSubscribed = false;
    updateBtn();
  })
  .catch(function(error) {
    console.log('Error unsubscribing', error);
  });
}

function initializeUI() {
  pushButton.addEventListener('click', function() {
    pushButton.disabled = true;
    if (isSubscribed) {
      unsubscribeUser();
    } else {
      subscribeUser();
    }
  });

  swRegistration.pushManager.getSubscription()
  .then(function(subscription) {
    isSubscribed = !(subscription === null);
    updateBtn();
  });
}

function updateBtn() {
  if (Notification.permission === 'denied') {
    pushButton.textContent = 'Push Messaging Blocked';
    pushButton.disabled = true;
    updateSubscriptionOnServer(null);
    return;
  }

  if (isSubscribed) {
    pushButton.textContent = 'Disable Push Messaging';
  } else {
    pushButton.textContent = 'Enable Push Messaging';
  }

  pushButton.disabled = false;
}

if ('serviceWorker' in navigator && 'PushManager' in window) {
  navigator.serviceWorker.register('${channel}/service_worker.js')
  .then(function(swReg) {
    swRegistration = swReg;
    initializeUI();
  })
  .catch(function(error) {
    console.error('Service Worker Error', error);
  });
} else {
  console.warn('Push messaging is not supported');
}
