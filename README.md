
run cli https://docs.stripe.com/stripe-cli/install

stripe login
stripe listen --forward-to localhost:8000/payment/stripe/webhook/