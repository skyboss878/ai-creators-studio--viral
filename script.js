paypal.Buttons({
  style: {
    shape: 'rect',
    color: 'gold',
    layout: 'vertical',
    label: 'subscribe'
  },
  createSubscription: function(data, actions) {
    return actions.subscription.create({
      plan_id: 'P-8DP70117TD556851YNA33XXA'  // Your PayPal plan ID
    });
  },
  onApprove: function(data, actions) {
    alert('Subscription successful! ID: ' + data.subscriptionID);

    // Optional: send subscription ID to backend for logging/verification
    /*
    fetch('/api/paypal-subscription', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subscriptionID: data.subscriptionID })
    }).then(res => res.json()).then(response => {
      console.log('Backend response:', response);
    }).catch(console.error);
    */
  }
}).render('#paypal-button-container');
