def detect_intent(query):
    """Detect the intent from user query and return appropriate response."""
    query = query.lower()
    
    if 'pension' in query:
        return """
        <h4>Pension Services</h4>
        <p>✅ To check your pension status:</p>
        <ol>
            <li>Enter your Aadhaar number above</li>
            <li>Click 'Search' to view status</li>
        </ol>
        <p>Need help? Call our pension helpline: 1800-XXX-XXXX</p>
        """
    
    elif 'ration' in query:
        return """
        <h4>Ration Card Services</h4>
        <p>✅ To check your ration card status:</p>
        <ol>
            <li>Enter your Aadhaar number above</li>
            <li>Click 'Search' to view details</li>
        </ol>
        <p>Need help? Visit your nearest ration shop or call: 1800-XXX-XXXX</p>
        """
    
    elif 'health' in query or 'insurance' in query:
        return """
        <h4>Health Insurance Services</h4>
        <p>✅ Available health schemes:</p>
        <ul>
            <li>Ayushman Bharat</li>
            <li>Senior Citizen Health Insurance</li>
            <li>State Health Insurance</li>
        </ul>
        <p>To apply: Enter your Aadhaar above and click 'Search'</p>
        """
    
    else:
        return """
        <h4>How can I help you?</h4>
        <p>I can assist you with:</p>
        <ul>
            <li>Pension services</li>
            <li>Ration card services</li>
            <li>Health insurance</li>
        </ul>
        <p>Please specify which service you need help with.</p>
        """ 