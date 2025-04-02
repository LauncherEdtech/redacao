import hmac
import hashlib
import json

# Cole aqui o JSON bruto do webhook (exatamente como a Kiwify envia)
json_payload = """
{
 "order_id":"637e8812-5730-4c4d-9378-c2013c1e2ba5","order_ref":"JQeAAIM","order_status":"paid","product_type":"membership","payment_method":"credit_card","store_id":"4L5dQkXtaYceSNP","payment_merchant_id":76151650,"installments":1,"card_type":"mastercard","card_last4digits":"1429","card_rejection_reason":null,"boleto_URL":null,"boleto_barcode":null,"boleto_expiry_date":null,"pix_code":null,"pix_expiration":null,"sale_type":"producer","created_at":"2025-04-02 05:09","updated_at":"2025-04-02 05:09","approved_date":"2025-04-03 05:09","refunded_at":null,"webhook_event_type":"order_approved","Product":{"product_id":"876ffb01-2305-480e-9b8f-13f16a35e53d","product_name":"Example product"},"Customer":{"full_name":"John Doe","first_name":"John","email":"johndoe@example.com","mobile":"+50524703593","CPF":"54254161570","ip":"1b95:cfb5:68d9:1f4c:d585:daf2:a69f:6bf6","instagram":"@kiwify","street":"Rua 1001","number":"315","complement":"SL 05","neighborhood":"Centro","city":"Balneário Camboriú","state":"SC","zipcode":"88330-756"},"Commissions":{"charge_amount":5298,"product_base_price":5298,"product_base_price_currency":"BRL","kiwify_fee":583,"kiwify_fee_currency":"BRL","settlement_amount":5298,"settlement_amount_currency":"BRL","sale_tax_rate":0,"sale_tax_amount":0,"commissioned_stores":[{"id":"8b8359a3-7cc1-40a3-b828-f54873bcdf2e","type":"producer","custom_name":"Example store","email":"example@store.domain","value":"4715"},{"id":"af0c8961-d0d3-4024-acf1-967414c6dea4","type":"coproducer","custom_name":"Example coproducer","email":"example@coproducer.domain","value":"4715"},{"id":"838fdb91-dbe1-4219-9925-b7b99652a2ac","type":"affiliate","affiliate_id":"vdTYqSK","custom_name":"Example affiliate","email":"example@affiliate.domain","value":"4715"}],"currency":"BRL","my_commission":4715,"funds_status":null,"estimated_deposit_date":null,"deposit_date":null},"TrackingParameters":{"src":null,"sck":null,"utm_source":null,"utm_medium":null,"utm_campaign":null,"utm_content":null,"utm_term":null},"Subscription":{"id":"3cb1a1b0-5aa1-4f5b-a09f-67ecfc0bddd3","start_date":"2025-03-30T05:09:32.747Z","next_payment":"2025-04-06T05:09:32.747Z","status":"active","plan":{"id":"f71116a9-bad1-4687-b775-39f5245ac233","name":"Example plan","frequency":"weekly","qty_charges":0},"charges":{"completed":[{"order_id":"637e8812-5730-4c4d-9378-c2013c1e2ba5","amount":4715,"status":"paid","installments":1,"card_type":"mastercard","card_last_digits":"4483","card_first_digits":"265471","created_at":"2025-03-30T05:09:32.747Z"}],"future":[{"charge_date":"2025-04-06T05:09:32.747Z"}]}},"subscription_id":"3cb1a1b0-5aa1-4f5b-a09f-67ecfc0bddd3","access_url":null
}
"""

# Cole aqui o mesmo segredo configurado no painel da Kiwify
segredo = "pe6r1p77lvt"

# Remove espaços extras do JSON e serializa como a Kiwify faz com JSON.stringify()
parsed = json.loads(json_payload)
normalized_payload = json.dumps(parsed, separators=(',', ':'))

# Gera assinatura HMAC-SHA1
assinatura = hmac.new(
    segredo.encode(),
    normalized_payload.encode(),
    hashlib.sha1
).hexdigest()

print("Assinatura calculada:", assinatura)
