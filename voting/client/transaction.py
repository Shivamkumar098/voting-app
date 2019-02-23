import hashlib
import base64
import random
import time
import requests
import yaml
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

# The Transaction Family Name
FAMILY_NAME = 'voting'
# TF Prefix is first 6 characters of SHA-512("cookiejar"), a4d219

def _hash(data):
    return hashlib.sha512(data).hexdigest()

def create_address(mode='user',name='name'):
     return _hash(FAMILY_NAME.encode())[:6]+_hash(mode.encode())[:6]+_hash(name.encode())[:58]


class VotingClient(object):
    '''Client Cookie Jar class

    Supports "bake", "eat", and "count" functions.
    '''

    def __init__(self, base_url, key_file=None):
        '''Initialize the client class.

           This is mainly getting the key pair and computing the address.
        '''
        self._base_url = base_url

        if key_file is None:
            self._signer = None
            return

        try:
            with open(key_file) as key_fd:
                private_key_str = key_fd.read().strip()
        except OSError as err:
            raise Exception(
                'Failed to read private key {}: {}'.format(
                    key_file, str(err)))

        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
        except ParseError as err:
            raise Exception( \
                'Failed to load private key: {}'.format(str(err)))

        self._signer = CryptoFactory(create_context('secp256k1')) \
            .new_signer(private_key)
        self._public_key = self._signer.get_public_key().as_hex()

    def vote(self,party,name):
     print('voting ........'+str(party)+'.....person..'+name)     
     paddr=create_address(mode='voting',name=party)
     uaddr=create_address(name=name)
     #self._wrap_and_send(paddr,"party",1,wait=10)
     #self._wrap_and_send(uaddr,"user", 1, wait=10)
     self._wrap_and_send(paddr,"vote", 1, wait=10,uaddress=uaddr)
     print('.......response........')
     
     
    def add(self,party):
        print('adding party.........'+str(' '.join(party)))
        paddr=create_address(mode='voting',name=' '.join(party))
        self._wrap_and_send(paddr,"create",0,wait=10)
        print('.............response.........')

    def list_parties(self,party):
        print('display parties .........')
        paddr=create_address(mode='voting',name=party)
        res = self._send_to_rest_api("state/{}".format(paddr))        
        try:
            ans= base64.b64decode(yaml.safe_load(res)["data"])
            print(party+' votes:',int(ans))
            return ans
        except BaseException:
            return None
        print('.........response.........')    
			
    def _send_to_rest_api(self, suffix, data=None, content_type=None):
        url = "{}/{}".format(self._base_url, suffix)
        print("URL to send to REST API is {}".format(url))

        headers = {}

        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if not result.ok:
                raise Exception("Error {}: {}".format(
                    result.status_code, result.reason))
        except requests.ConnectionError as err:
            raise Exception(
                'Failed to connect to {}: {}'.format(url, str(err)))
        except BaseException as err:
            raise Exception(err)

        return result.text

    def _wait_for_status(self, batch_id, wait, result):
        if wait and wait > 0:
            waited = 0
            start_time = time.time()
            while waited < wait:
                result = self._send_to_rest_api("batch_statuses?id={}&wait={}"
                                               .format(batch_id, wait))
                status = yaml.safe_load(result)['data'][0]['status']
                waited = time.time() - start_time

                if status != 'PENDING':
                    return result
            return "Transaction timed out after waiting {} seconds." \
               .format(wait)
        else:
            return result


    def _wrap_and_send(self,address,action, amount, wait=None,uaddress=''):
        raw_payload = ",".join([action, str(amount)])
        payload = raw_payload.encode()
        input_and_output_address_list=[]
        if uaddress=='':
            input_and_output_address_list = [address]
        else:
            input_and_output_address_list=[address,uaddress]    
        header = TransactionHeader(
            signer_public_key=self._public_key,
            family_name=FAMILY_NAME,
            family_version="1.0",
            inputs=input_and_output_address_list,
            outputs=input_and_output_address_list,
            dependencies=[],
            payload_sha512=_hash(payload),
            batcher_public_key=self._public_key,
            nonce=random.random().hex().encode()
        ).SerializeToString()

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=self._signer.sign(header)
        )

        transaction_list = [transaction]

        header = BatchHeader(
            signer_public_key=self._public_key,
            transaction_ids=[txn.header_signature for txn in transaction_list]
        ).SerializeToString()

        batch = Batch(
            header=header,
            transactions=transaction_list,
            header_signature=self._signer.sign(header))

        batch_list = BatchList(batches=[batch])
        batch_id = batch_list.batches[0].header_signature

        result = self._send_to_rest_api("batches",
                                       batch_list.SerializeToString(),
                                       'application/octet-stream')

        return self._wait_for_status(batch_id, wait, result)
