# Y^2=x^3 + ax + b
import hashlib, math, string, secrets, random, struct



class ECC:
        def __init__(self, passphrase=None, key_pub=None, key_priv=None):
                self.key_pub = key_pub
                self.passphrase = passphrase
                self.key_priv = key_priv
                self.equation = 'y^2 = x^3 + x + 17'
                self.Gx = 669946410810288267923
                self.Gy = math.sqrt(300690837210381833369313537783291486597495264719978640366727407)
                self.a = 1
                self.b = 17
                self.p = 13
                # '2^256 - 2^32 - 2^9 - 2^8 - 2^7 - 2^6 - 2^4 - 1'
        
        
        def gen_passphrase(self, length=22):
                characters = string.ascii_letters + string.digits + string.punctuation
                password = ''.join(secrets.choice(characters) for _ in range(length))
                return password
                
        def gen_private_key(self, password:str=None):
                if password == None:
                        password = self.gen_passphrase().encode()
                else:
                        password.encode()
                encrypted_password = hashlib.sha256(password).digest()
                private_key = int.from_bytes(encrypted_password, 'big')
                return private_key
        
        def gen_keys(self, private_key):
                verify = False
                while verify == False:
                        Px = private_key * self.Gx
                        Py = private_key * self.Gy
                        Qy_sqrd = Py**2
                        Qx_cubed = Px**3+self.b
                        modp_Qx = Qx_cubed % self.p
                        modp_Qy = Qy_sqrd % self.p
                        #print(f'{modp_Qx}   {modp_Qy}')
                        if modp_Qx == modp_Qy:
                                verify = True
                        else:
                                private_key = self.gen_private_key()
			
                return {'public':(Px,Py), 'private': private_key}
        
        def verify(self, Px:int, Py:int, private_key:int):
                Qy_sqrd = Py**2
                Qx_cubed = Px**3+self.b
                modp_Qx = Qx_cubed % self.p
                modp_Qy = Qy_sqrd % self.p
                
                #print(f'{modp_Qx}    {modp_Qy}')
                
                P2x = private_key * self.Gx
                P2y = private_key * self.Gy
                if Px == P2x and Py == P2y and modp_Qx == modp_Qy:
                        return True
                
                
        def hexi(self, data:str):
                data = bytes.hex(str(data).encode())
                return data
        
#     Take the y-coordinate (Qy) of the public key and square it.
#         This represents the left-hand side of the equation: Qy^2.

#     Take the x-coordinate (Qx) of the public key and cube it (raise it to the power of 3).
#         Multiply the result by Qx.
#         Multiply the curve coefficient 'a' by Qx.
#         Add the curve constant 'b'.
#         This represents the right-hand side of the equation: Qx^3 + aQx + b.

#     Check if the left-hand side (Qy^2) is congruent (equivalent) to the right-hand side (Qx^3 + aQx + b) modulo a prime number 'p'.
#         Modulo 'p' means finding the remainder when dividing by 'p'.
#         If the remainders of the left-hand side and right-hand side are the same when divided by 'p', then the point is considered valid and lies on the curve.

# If the left-hand side is congruent to the right-hand side modulo 'p', the public key is considered valid. If they are not congruent, the public key is not valid.


ecc = ECC()
pub = ecc.gen_keys(10000031003493204932410)
priv = pub['private']
print(f'privatekey: {priv}')
pub_e = ecc.hexi(str(pub['public']))
print(f'hex version of public key: {pub_e}')
pub = pub['public']
Px,Py = pub
verify = ecc.verify(Px, Py, private_key=priv)
print(f'valid key pair: {verify}')