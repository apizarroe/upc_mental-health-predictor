"""
Fuente única de keywords para detección de depresión y ansiedad.
Todos los módulos (pipeline, entrenamiento, etiquetado, preprocesador) importan desde aquí.

Señales de riesgo extremo (ideación suicida, autolesión, crisis severa) NO están aquí —
están en risk_detector.py donde se aplica manejo de negación determinista.
"""

DEPRESSION_KEYWORDS = {
    # Frases del dataset real — variantes masculino/femenino (peso 2)
    'me siento muy triste': 2, 'me siento triste': 2,
    'me he sentido muy triste': 2, 'me he sentido triste': 2, 'me he sentido solo': 2, 'me he sentido sola': 2,
    'me siento tan perdida': 2, 'me siento tan perdido': 2,
    'me siento perdido': 2, 'me siento perdida': 2,
    'siento que ya no': 2, 'siento que no importa': 2,
    'siento que he perdido': 2, 'siento que no soy': 2,
    'no puedo evitar sentirme': 2, 'siento que estoy atrapado': 2,
    'siento que estoy atrapada': 2,
    'ya no sé qué': 2, 'ya no sé cómo': 2,
    'estoy cansado de': 2, 'estoy cansada de': 2,
    'me siento solo': 2, 'me siento sola': 2,
    'me siento vacío': 2, 'me siento vacía': 2,
    'me siento un fracaso': 2, 'no quiero seguir': 2,
    'me siento culpable': 2, 'me siento avergonzado': 2, 'me siento avergonzada': 2,
    'dolor emocional': 2, 'no vale la pena': 2, 'sin esperanza': 2,
    'perdí las ganas': 2, 'me siento invisible': 2,
    'nadie me entiende': 2, 'quisiera desaparecer': 2,
    'me da igual todo': 2, 'todo me cuesta': 2,
    'ya no disfruto': 2, 'no encuentro sentido': 2,
    'siento que no tiene sentido': 2, 'me siento muy sola': 2, 'me siento muy solo': 2,
    # DSM-5: Anhedonia — pérdida de interés o placer (no solapan con ansiedad)
    'nada me alegra': 2, 'perdí el interés': 2, 'ya no me importa nada': 2,
    'no siento nada': 2, 'nada me da placer': 2, 'ya no me da alegría': 2,
    # DSM-5: Cambios cognitivos (excluye 'no puedo concentrarme', ya en ansiedad)
    'no puedo pensar': 2, 'me cuesta concentrarme': 2, 'me cuesta tomar decisiones': 2,
    'no recuerdo nada': 1, 'mente en blanco': 1,
    # DSM-5: Cambios somáticos — apetito y sueño (excluye 'no puedo dormir', ya en ansiedad)
    'no tengo apetito': 2, 'no puedo comer': 2, 'duermo demasiado': 1,
    'me cuesta levantarme': 1, 'no tengo hambre': 1,
    # DSM-5: Aislamiento social
    'me alejo de todos': 2, 'no quiero ver a nadie': 2, 'me encierro en casa': 2,
    'evito salir': 1, 'prefiero estar solo': 1, 'prefiero estar sola': 1, 'me aíslo': 1,
    # Palabras exclusivas (peso 1)
    'anhedonia': 1, 'desesperanza': 1, 'apatía': 1, 'desgano': 1,
    'melancolía': 1, 'autoculpa': 1, 'abatido': 1, 'abatida': 1,
    'desanimado': 1, 'desanimada': 1, 'hundido': 1, 'hundida': 1,
    'desvalido': 1, 'resignado': 1, 'resignada': 1,
    'decaído': 1, 'decaída': 1, 'letárgico': 1, 'letárgica': 1,
    # Síntomas físicos y cognitivos de depresión (peso 1)
    'agotado': 1, 'agotada': 1, 'sin energía': 1, 'sin fuerzas': 1,
    'sin motivación': 1, 'sin ganas': 1, 'desesperado': 1, 'desesperada': 1,
    'triste': 1, 'tristeza': 1, 'lloro': 1, 'llorar': 1, 'llorando': 1,
    'vacío': 1, 'vacía': 1, 'inútil': 1,
}

ANXIETY_KEYWORDS = {
    # Frases del dataset real — variantes masculino/femenino (peso 2)
    'me siento ansioso': 2, 'me siento ansiosa': 2,
    'me siento muy ansioso': 2, 'me siento muy ansiosa': 2,
    'estoy ansioso': 2, 'estoy ansiosa': 2,
    'constantemente preocupado': 2, 'constantemente preocupada': 2,
    'siento que estoy constantemente': 2,
    'no puedo deshacerme de': 2, 'no puedo evitar sentir': 2,
    'no puedo escapar': 2, 'tengo miedo de que': 2,
    'me siento abrumado': 2, 'me siento abrumada': 2,
    'me siento abrumado por': 2, 'me siento abrumada por': 2,
    'siento que me estoy': 2, 'pensamientos negativos': 2,
    'no puedo concentrarme': 2, 'no puedo dormir': 2,
    'siento que pierdo el control': 2, 'siento que algo malo': 2,
    'mi mente no para': 2, 'no puedo relajarme': 2,
    'me cuesta respirar': 2, 'siento el corazón acelerado': 2,
    'no puedo con tanto': 2, 'todo me genera angustia': 2,
    # Frases de ansiedad laboral/situacional (peso 2)
    'bajo mucha presión': 2, 'bajo una presión': 2,
    'fuente de estrés': 2, 'mucho estrés': 2, 'demasiado estrés': 2,
    'estrés constante': 2, 'constantemente estresado': 2, 'constantemente estresada': 2,
    'no puedo tomar un descanso': 2, 'no puedo descansar': 2,
    'lucha constante': 2, 'siento como si estuviera constantemente': 2,
    'afectando mi bienestar': 2, 'afecta mi salud mental': 2,
    'me resulta difícil': 2, 'difícil mantener el equilibrio': 2,
    # DSM-5: Ataques de pánico (no solapan con depresión)
    'ataque de pánico': 2, 'siento que me voy a desmayar': 2,
    'siento que me voy a morir': 2, 'me da un ataque de ansiedad': 2,
    # DSM-5: Evitación conductual
    'evito situaciones': 2, 'tengo miedo de salir': 2, 'me da miedo la gente': 2,
    'evito lugares': 2,
    # DSM-5: Síntomas físicos de ansiedad (excluye 'siento el corazón acelerado', ya existe)
    'me tiemblan las manos': 2, 'nudo en el estómago': 2,
    'me duele el pecho': 1, 'sudo de los nervios': 1,
    # DSM-5: Preocupación anticipatoria
    'no puedo dejar de pensar': 2, 'siempre espero lo peor': 2,
    'me anticipo al desastre': 1, 'todo puede salir mal': 1,
    # Palabras exclusivas (peso 1)
    'hiperventilación': 1, 'taquicardia': 1, 'rumiación': 1, 'catastrofismo': 1,
    'pánico': 1, 'angustia': 1, 'inquietud': 1, 'hipervigilancia': 1,
    'irritabilidad': 1, 'temor constante': 1, 'ansiedad': 1, 'estrés': 1,
    # Síntomas físicos y cognitivos de ansiedad (peso 1)
    'inquieto': 1, 'inquieta': 1, 'nervioso': 1, 'nerviosa': 1,
    'preocupación': 1, 'tensión': 1, 'sobresaltado': 1, 'sobresaltada': 1,
}
