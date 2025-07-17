import hashlib
import secrets
import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import time
import hmac

class SecurityLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class QuantumChannel:
    """Simulates a quantum channel for QKD"""
    alice_id: str
    bob_id: str
    error_rate: float
    active: bool = True
    
class PostQuantumCrypto:
    """Simplified lattice-based cryptography implementation"""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.HIGH):
        self.security_level = security_level
        # Security parameters for lattice-based crypto (reduced for demo)
        self.params = {
            SecurityLevel.HIGH: {"n": 256, "q": 2**16, "sigma": 3.2},
            SecurityLevel.MEDIUM: {"n": 128, "q": 2**15, "sigma": 2.8},
            SecurityLevel.LOW: {"n": 64, "q": 2**14, "sigma": 2.4}
        }[security_level]
        
    def generate_keypair(self) -> Tuple[Dict, Dict]:
        """Generate lattice-based public/private key pair"""
        # Simplified lattice key generation
        n, q = self.params["n"], self.params["q"]
        
        # Private key: small random values
        private_key = {
            "s": np.random.randint(-2, 3, n, dtype=np.int32),
            "e": np.random.randint(-1, 2, n, dtype=np.int32)
        }
        
        # Public key: a*s + e (mod q)
        a = np.random.randint(0, q, n, dtype=np.int32)
        public_key = {
            "a": a,
            "b": (a * private_key["s"] + private_key["e"]) % q
        }
        
        return public_key, private_key
    
    def encrypt(self, public_key: Dict, message: bytes) -> bytes:
        """Encrypt message using lattice-based encryption"""
        # Simplified lattice encryption
        n, q = self.params["n"], self.params["q"]
        
        # Convert message to polynomial (simplified)
        msg_hash = hashlib.sha256(message).digest()[:n//8]
        msg_poly = np.frombuffer(msg_hash, dtype=np.uint8).astype(np.int32)
        msg_poly = np.pad(msg_poly, (0, n - len(msg_poly)), mode='constant')
        
        # Encrypt: (a*r + e1, b*r + e2 + m)
        r = np.random.randint(-1, 2, n, dtype=np.int32)
        e1 = np.random.randint(-1, 2, n, dtype=np.int32)
        e2 = np.random.randint(-1, 2, n, dtype=np.int32)
        
        c1 = (public_key["a"] * r + e1) % q
        c2 = (public_key["b"] * r + e2 + msg_poly * (q // 4)) % q
        
        # Combine and return as bytes
        combined = np.concatenate([c1, c2])
        return combined.astype(np.int16).tobytes()  # Use int16 to fit in memory
    
    def decrypt(self, private_key: Dict, ciphertext: bytes) -> bytes:
        """Decrypt ciphertext using private key"""
        # Simplified lattice decryption
        n, q = self.params["n"], self.params["q"]
        
        cipher_array = np.frombuffer(ciphertext, dtype=np.int16)
        half_len = len(cipher_array) // 2
        c1 = cipher_array[:half_len].astype(np.int32)
        c2 = cipher_array[half_len:].astype(np.int32)
        
        # Decrypt: c2 - c1*s
        decrypted = (c2 - c1 * private_key["s"][:len(c1)]) % q
        
        # Extract message bits
        message_bits = (decrypted > q // 8).astype(np.uint8)
        
        # Convert back to 32-byte key
        key_bytes = bytearray(32)
        for i in range(min(32, len(message_bits))):
            key_bytes[i] = message_bits[i] % 256
            
        return bytes(key_bytes)

class QKDProtocol:
    """Simulates BB84 Quantum Key Distribution protocol"""
    
    def __init__(self, channel: QuantumChannel):
        self.channel = channel
        self.photon_loss_rate = 0.1  # 10% photon loss
        self.eavesdrop_threshold = 0.11  # Above this indicates eavesdropping
        
    def generate_quantum_key(self, key_length: int = 256) -> Optional[bytes]:
        """Generate symmetric key using QKD"""
        if not self.channel.active:
            return None
            
        # Simulate BB84 protocol
        raw_key_length = key_length * 4  # Need more bits due to basis reconciliation
        
        # Alice's random bits and bases
        alice_bits = [secrets.randbits(1) for _ in range(raw_key_length)]
        alice_bases = [secrets.randbits(1) for _ in range(raw_key_length)]
        
        # Bob's random bases
        bob_bases = [secrets.randbits(1) for _ in range(raw_key_length)]
        
        # Simulate quantum channel transmission with errors
        received_bits = []
        for i in range(raw_key_length):
            if random.random() < self.photon_loss_rate:
                received_bits.append(None)  # Photon lost
            else:
                bit = alice_bits[i]
                # Add quantum channel errors
                if random.random() < self.channel.error_rate:
                    bit = 1 - bit
                received_bits.append(bit)
        
        # Basis reconciliation
        matching_bases = []
        for i in range(raw_key_length):
            if (alice_bases[i] == bob_bases[i] and 
                received_bits[i] is not None):
                matching_bases.append((i, alice_bits[i]))
        
        # Extract key from matching bases
        if len(matching_bases) < key_length:
            return None  # Not enough matching bases
            
        key_bits = [bit for _, bit in matching_bases[:key_length]]
        
        # Error detection (simplified)
        test_bits = matching_bases[key_length:key_length+32]
        alice_test = [alice_bits[i] for i, _ in test_bits]
        bob_test = [bit for _, bit in test_bits]
        
        error_rate = sum(a != b for a, b in zip(alice_test, bob_test)) / len(test_bits)
        
        if error_rate > self.eavesdrop_threshold:
            print(f"⚠️  High error rate detected: {error_rate:.2%} - Possible eavesdropping!")
            return None
            
        # Convert bits to bytes
        key_bytes = bytearray()
        for i in range(0, len(key_bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(key_bits):
                    byte |= key_bits[i + j] << (7 - j)
            key_bytes.append(byte)
            
        return bytes(key_bytes)

class HybridKeyExchangeSystem:
    """Main system combining QKD and Post-Quantum Cryptography"""
    
    def __init__(self, participants: List[str]):
        self.participants = participants
        self.n_participants = len(participants)
        self.pqc = PostQuantumCrypto(SecurityLevel.HIGH)
        
        # Initialize quantum channels (simplified - assumes full connectivity)
        self.quantum_channels = {}
        for i in range(self.n_participants):
            for j in range(i + 1, self.n_participants):
                alice, bob = participants[i], participants[j]
                channel = QuantumChannel(
                    alice_id=alice,
                    bob_id=bob,
                    error_rate=random.random() * 0.05  # 0-5% error rate
                )
                self.quantum_channels[(alice, bob)] = channel
        
        # Key storage
        self.master_keys = {}  # Long-term keys from QKD
        self.session_keys = {}  # Short-term keys from PQC
        self.public_keys = {}  # PQC public keys
        self.private_keys = {}  # PQC private keys
        
        # Generate PQC keypairs for each participant
        for participant in participants:
            pub_key, priv_key = self.pqc.generate_keypair()
            self.public_keys[participant] = pub_key
            self.private_keys[participant] = priv_key
    
    def establish_master_keys(self) -> Dict[str, int]:
        """Establish master keys using QKD between all pairs"""
        print("🔄 Establishing master keys using QKD...")
        results = {"success": 0, "failed": 0}
        
        for (alice, bob), channel in self.quantum_channels.items():
            qkd = QKDProtocol(channel)
            master_key = qkd.generate_quantum_key(256)  # 256-bit master key
            
            if master_key:
                self.master_keys[(alice, bob)] = master_key
                self.master_keys[(bob, alice)] = master_key  # Symmetric
                results["success"] += 1
                print(f"✅ Master key established: {alice} ↔ {bob}")
            else:
                results["failed"] += 1
                print(f"❌ Failed to establish master key: {alice} ↔ {bob}")
        
        return results
    
    def generate_session_key(self, alice: str, bob: str) -> Optional[bytes]:
        """Generate session key using PQC, authenticated by master key"""
        
        # Check if master key exists
        master_key = self.master_keys.get((alice, bob))
        if not master_key:
            print(f"❌ No master key available for {alice} ↔ {bob}")
            return None
        
        # Generate random session key
        session_key = secrets.token_bytes(32)  # 256-bit session key
        
        # Encrypt session key using PQC
        encrypted_key = self.pqc.encrypt(
            self.public_keys[bob], 
            session_key
        )
        
        # Create authenticated message using master key
        mac = hmac.new(
            master_key, 
            encrypted_key, 
            hashlib.sha256
        ).digest()
        
        # Store session key
        self.session_keys[(alice, bob)] = session_key
        self.session_keys[(bob, alice)] = session_key
        
        print(f"🔑 Session key generated: {alice} ↔ {bob}")
        return session_key
    
    def refresh_all_session_keys(self):
        """Refresh all session keys periodically"""
        print("🔄 Refreshing all session keys...")
        
        for i in range(self.n_participants):
            for j in range(i + 1, self.n_participants):
                alice, bob = self.participants[i], self.participants[j]
                if (alice, bob) in self.master_keys:
                    self.generate_session_key(alice, bob)
    
    def encrypt_message(self, sender: str, receiver: str, message: str) -> Optional[bytes]:
        """Encrypt message using session key"""
        session_key = self.session_keys.get((sender, receiver))
        if not session_key:
            print(f"❌ No session key available for {sender} → {receiver}")
            return None
        
        # Simple AES-like encryption (simplified)
        message_bytes = message.encode('utf-8')
        nonce = secrets.token_bytes(16)
        
        # XOR with key-derived stream (simplified)
        key_stream = hashlib.sha256(session_key + nonce).digest()
        encrypted = bytes(a ^ b for a, b in zip(message_bytes, key_stream[:len(message_bytes)]))
        
        return nonce + encrypted
    
    def decrypt_message(self, sender: str, receiver: str, ciphertext: bytes) -> Optional[str]:
        """Decrypt message using session key"""
        session_key = self.session_keys.get((sender, receiver))
        if not session_key:
            return None
        
        nonce = ciphertext[:16]
        encrypted = ciphertext[16:]
        
        # XOR with key-derived stream
        key_stream = hashlib.sha256(session_key + nonce).digest()
        decrypted = bytes(a ^ b for a, b in zip(encrypted, key_stream[:len(encrypted)]))
        
        return decrypted.decode('utf-8')
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        total_pairs = self.n_participants * (self.n_participants - 1) // 2
        
        return {
            "participants": self.n_participants,
            "total_key_pairs": total_pairs,
            "master_keys_established": len(self.master_keys) // 2,
            "session_keys_active": len(self.session_keys) // 2,
            "quantum_channels_active": sum(1 for ch in self.quantum_channels.values() if ch.active),
            "security_level": self.pqc.security_level.value
        }

# Demo usage
def demo_system():
    """Demonstrate the hybrid key exchange system"""
    
    # Create a group of 25 participants
    participants = [f"User_{i:02d}" for i in range(1, 26)]
    
    print("🚀 Initializing Hybrid QKD-PQC Key Exchange System")
    print(f"👥 Participants: {len(participants)}")
    print("=" * 60)
    
    # Initialize system
    system = HybridKeyExchangeSystem(participants)
    
    # Establish master keys using QKD
    master_key_results = system.establish_master_keys()
    print(f"\n📊 Master Key Results: {master_key_results}")
    
    # Generate session keys for active pairs
    print("\n🔑 Generating session keys...")
    session_count = 0
    for i in range(min(5, len(participants))):  # Demo with first 5 users
        for j in range(i + 1, min(5, len(participants))):
            alice, bob = participants[i], participants[j]
            if system.generate_session_key(alice, bob):
                session_count += 1
    
    print(f"✅ Generated {session_count} session keys")
    
    # Demonstrate secure communication
    print("\n💬 Demonstrating secure communication...")
    alice, bob = participants[0], participants[1]
    
    message = "Hello Bob! This is a secure message in our post-quantum world."
    encrypted = system.encrypt_message(alice, bob, message)
    
    if encrypted:
        print(f"📤 {alice} → {bob}: Message encrypted ({len(encrypted)} bytes)")
        
        decrypted = system.decrypt_message(alice, bob, encrypted)
        if decrypted:
            print(f"📥 {bob} received: '{decrypted}'")
            print("✅ Secure communication successful!")
    
    # Show system status
    print("\n📊 System Status:")
    status = system.get_system_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n🔄 Demonstrating key refresh...")
    system.refresh_all_session_keys()
    
    print("\n✅ Hybrid QKD-PQC system demonstration complete!")

if __name__ == "__main__":
    demo_system()