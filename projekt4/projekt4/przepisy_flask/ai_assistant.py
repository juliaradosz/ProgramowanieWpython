"""Asystent kulinarny AI oparty o model Groq (llama).

To komponent "wychodzący poza zakres" pierwotnego projektu strony z
przepisami – czat z asystentem AI, który odpowiada na pytania kulinarne,
proponuje zamienniki składników, przelicza porcje itp.

Integracja korzysta z oficjalnego SDK ``groq`` i modelu
``llama-3.3-70b-versatile`` (konfigurowalnego). Jeśli klucz API nie jest
ustawiony, asystent działa w trybie offline – zwraca uprzejmą informację
zamiast odpowiedzi modelu.
"""

from __future__ import annotations

SYSTEM_PROMPT = (
    "Jesteś pomocnym asystentem kulinarnym na polskiej stronie z przepisami "
    "'Przepisy Kulinarne'. Odpowiadasz wyłącznie po polsku, zwięźle i "
    "rzeczowo. Pomagasz w gotowaniu: proponujesz przepisy i zamienniki "
    "składników, przeliczasz proporcje na inną liczbę porcji, doradzasz przy "
    "doborze dań, tłumaczysz techniki kulinarne i podpowiadasz czas oraz "
    "temperaturę. Jeśli pytanie nie dotyczy gotowania, jedzenia ani "
    "prowadzenia kuchni, grzecznie poinformuj, że pomagasz tylko w sprawach "
    "kulinarnych. Nie podawaj porad medycznych. Formatuj odpowiedzi czytelnie "
    "(listy, krótkie akapity)."
)

_MAX_TOKENS = 1024


class ChatAssistant:
    """Cienka warstwa nad SDK Groq udostępniająca metodę :meth:`reply`."""

    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        self._client = None
        if api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=api_key)
            except Exception:
                self._client = None

    @property
    def available(self) -> bool:
        """Czy skonfigurowano klucz API i klienta (tryb online)?"""
        return self._client is not None

    def reply(
        self,
        history: list[dict[str, str]],
        user_message: str,
        recipe_context: str | None = None,
    ) -> str:
        """Zwraca odpowiedź asystenta na wiadomość użytkownika.

        Args:
            history: dotychczasowa rozmowa jako lista {"role", "content"}
                (role: "user" lub "assistant").
            user_message: nowa wiadomość użytkownika.
            recipe_context: opcjonalny opis przepisu, którego dotyczy rozmowa.

        Returns:
            Tekst odpowiedzi asystenta.
        """
        if not self.available:
            return self._offline_reply()

        # Budujemy historię – Groq używa tego samego formatu co OpenAI.
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for m in history:
            if m.get("content"):
                messages.append({"role": m["role"], "content": m["content"]})

        # Jeśli jest kontekst przepisu, dołącz go do wiadomości użytkownika.
        full_message = user_message
        if recipe_context:
            full_message = (
                f"Kontekst – użytkownik przegląda przepis:\n{recipe_context}"
                f"\n\nPytanie: {user_message}"
            )

        messages.append({"role": "user", "content": full_message})

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=_MAX_TOKENS,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            return (
                "Przepraszam, nie udało się połączyć z asystentem AI "
                f"({type(exc).__name__}). Spróbuj ponownie za chwilę."
            )

    @staticmethod
    def _offline_reply() -> str:
        """Odpowiedź zastępcza, gdy brak skonfigurowanego klucza API."""
        return (
            "Asystent AI jest obecnie wyłączony – administrator nie ustawił "
            "klucza API (zmienna GROQ_API_KEY). Po jego skonfigurowaniu "
            "będę odpowiadać na pytania kulinarne: zamienniki składników, "
            "przeliczanie porcji, dobór dań i techniki gotowania."
        )