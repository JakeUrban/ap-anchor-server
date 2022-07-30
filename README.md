# AP Anchor Server

This is a reference implementation of an Anchor Server using the [Anchor Platform].

[Anchor Platform]: https://github.com/stellar/java-stellar-anchor-sdk/tree/main/docs

## Run it

```shell
cp .env.example .env
docker compose build
docker compose up
```

You now have the Anchor Platform running on http://localhost:8080.

## Test it

1. Go to https://demo-wallet.stellar.org
2. Select "Add Asset" and choose SRT
3. Select "SEP-24 Deposit" from the dropdown
4. Complete the UX
5. You'll receive a payment of SRT
6. Override the home domain to localhost:8080
7. Select "SEP-31 Send" from the dropdown
8. Enter the customer info
9. The demo wallet will send some SRT to the Anchor Platform
10. The Anchor Platform will complete your transaction
