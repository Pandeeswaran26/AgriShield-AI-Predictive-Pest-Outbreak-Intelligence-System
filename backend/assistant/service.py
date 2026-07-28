def get_ai_response(message: str) -> str:

    message = message.lower()

    if "cotton" in message:
        return (
            "Cotton crops are commonly affected by aphids, whiteflies, "
            "bollworms, and jassids. Regular field inspections and "
            "integrated pest management practices are recommended."
        )

    elif "rice" in message:
        return (
            "Rice crops are susceptible to stem borers, brown planthoppers, "
            "and leaf folders. Maintain proper water management and monitor "
            "fields frequently."
        )

    elif "pest" in message:
        return (
            "Early pest detection is important. Monitor crops regularly, "
            "use pheromone traps, and follow integrated pest management practices."
        )

    elif "weather" in message:
        return (
            "Weather conditions strongly influence pest outbreaks. High humidity "
            "and rainfall often increase pest activity."
        )

    else:
        return (
            "I am AgriShield AI Assistant. Ask me about crops, pests, weather, "
            "or disease prevention."
        )