"""
SIP Phone Calling Configuration for VoiceAI India

This file configures LiveKit's SIP integration so your agent
can make and receive real phone calls via Indian SIP providers.

SETUP STEPS (when you're ready to go paid):
1. Sign up with an Indian SIP provider:
   - FreJun (frejun.com) — starts Rs.1,299/mo
   - Exotel (exotel.com) — popular in India
   - CloudBharat (cloudbharat.in) — Indian VoIP
   - Knowlarity (knowlarity.com) — enterprise option

2. Get your SIP credentials:
   - SIP server address (e.g., sip.provider.com)
   - Username
   - Password
   - Phone number (+91XXXXXXXXXX)

3. Install LiveKit CLI:
   Download from: https://github.com/livekit/livekit-cli/releases

4. Create the SIP trunk:
   lk sip trunk create \\
     --inbound \\
     --name "india-inbound" \\
     --numbers "+91XXXXXXXXXX" \\
     --auth-username "your-sip-username" \\
     --auth-password "your-sip-password"

5. Create a dispatch rule (routes calls to your agent):
   lk sip dispatch create \\
     --trunk "india-inbound" \\
     --dispatch-to agent

FREE TESTING OPTIONS:
- Use LiveKit Playground (browser) — already working!
- Use a free SIP softphone (MicroSIP on Windows):
  1. Download MicroSIP from microsip.org
  2. Configure with your LiveKit SIP URI
  3. Call your agent from the softphone
"""

import os
from dataclasses import dataclass


@dataclass
class SIPConfig:
    """SIP trunk configuration for Indian telephony."""
    provider: str = ""
    server: str = ""
    username: str = ""
    password: str = ""
    phone_number: str = ""
    port: int = 5060
    transport: str = "UDP"  # UDP, TCP, or TLS

    # LiveKit SIP URI (from your project settings)
    livekit_sip_uri: str = "sip:33i2cd8fry5.sip.livekit.cloud"

    # TRAI number series
    number_series: str = "1600"  # 1600 for service, 140 for promotional

    @property
    def is_configured(self) -> bool:
        return bool(self.server and self.username and self.phone_number)


# Pre-configured templates for popular Indian SIP providers
PROVIDER_TEMPLATES = {
    "frejun": SIPConfig(
        provider="FreJun",
        server="sip.frejun.com",
        port=5060,
        transport="UDP",
    ),
    "exotel": SIPConfig(
        provider="Exotel",
        server="sip.exotel.com",
        port=5060,
        transport="TLS",
    ),
    "cloudbharat": SIPConfig(
        provider="CloudBharat",
        server="sip.cloudbharat.in",
        port=5060,
        transport="UDP",
    ),
    "knowlarity": SIPConfig(
        provider="Knowlarity",
        server="sip.knowlarity.com",
        port=5060,
        transport="TLS",
    ),
}


def get_sip_config() -> SIPConfig:
    """Load SIP config from environment variables."""
    return SIPConfig(
        provider=os.getenv("SIP_PROVIDER", ""),
        server=os.getenv("SIP_SERVER", ""),
        username=os.getenv("SIP_USERNAME", ""),
        password=os.getenv("SIP_PASSWORD", ""),
        phone_number=os.getenv("SIP_PHONE_NUMBER", ""),
    )


def print_setup_guide():
    """Print SIP setup instructions."""
    print("""
╔══════════════════════════════════════════════════╗
║  VoiceAI India — SIP Phone Setup Guide           ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  Step 1: Choose a provider                       ║
║    - FreJun: Rs.1,299/mo (frejun.com)           ║
║    - Exotel: Custom pricing (exotel.com)        ║
║    - CloudBharat: Affordable (cloudbharat.in)   ║
║                                                  ║
║  Step 2: Add to .env file                        ║
║    SIP_PROVIDER=frejun                           ║
║    SIP_SERVER=sip.frejun.com                     ║
║    SIP_USERNAME=your_username                    ║
║    SIP_PASSWORD=your_password                    ║
║    SIP_PHONE_NUMBER=+919876543210               ║
║                                                  ║
║  Step 3: Create LiveKit SIP trunk                ║
║    lk sip trunk create --inbound ...             ║
║                                                  ║
║  Step 4: Test!                                   ║
║    Call +919876543210 from any phone             ║
║                                                  ║
║  Your LiveKit SIP URI:                           ║
║    sip:33i2cd8fry5.sip.livekit.cloud            ║
║                                                  ║
╚══════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    config = get_sip_config()
    if config.is_configured:
        print(f"SIP configured: {config.provider} ({config.phone_number})")
    else:
        print_setup_guide()