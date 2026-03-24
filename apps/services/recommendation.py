# from django.db.models import Q
# from .models import Doctor


# class DoctorRecommendationEngine:
#     """
#     Intelligent recommendation system for suggesting doctors to patients.
    
#     Features:
#     1. Recommend by specialization
#     2. Recommend by price range
#     3. Recommend top-rated doctors
#     4. Recommend experienced doctors
#     5. Smart search functionality
#     6. Similar doctor suggestions
#     """
    
#     def __init__(self):
#         """Initialize with all available doctors."""
#         self.doctors = Doctor.objects.all()
    
#     def recommend_by_specialization(self, specialization, limit=5):
#         """
#         Recommend top doctors in a specific specialization.
        
#         Args:
#             specialization (str): Medical specialization
#             limit (int): Number of recommendations
            
#         Returns:
#             QuerySet: Top-rated doctors in that specialty
#         """
#         return self.doctors.filter(
#             specialization=specialization,
#             is_available_online=True
#         ).order_by('-rating', '-years_of_experience')[:limit]
    
#     def recommend_by_price_range(self, min_price=0, max_price=10000, limit=10):
#         """
#         Recommend doctors within a specific price range.
        
#         Args:
#             min_price (float): Minimum consultation fee
#             max_price (float): Maximum consultation fee
#             limit (int): Number of recommendations
            
#         Returns:
#             QuerySet: Doctors within price range, ordered by rating
#         """
#         return self.doctors.filter(
#             consultation_fee__gte=min_price,
#             consultation_fee__lte=max_price,
#             is_available_online=True
#         ).order_by('consultation_fee', '-rating')[:limit]
    
#     def recommend_top_rated(self, min_rating=4.0, limit=10):
#         """
#         Get highest-rated doctors.
        
#         Args:
#             min_rating (float): Minimum rating threshold
#             limit (int): Number of recommendations
            
#         Returns:
#             QuerySet: Top-rated available doctors
#         """
#         return self.doctors.filter(
#             is_available_online=True,
#             rating__gte=min_rating
#         ).order_by('-rating', '-total_reviews')[:limit]
    
#     def recommend_by_experience(self, min_years=5, limit=10):
#         """
#         Recommend experienced doctors.
        
#         Args:
#             min_years (int): Minimum years of experience
#             limit (int): Number of recommendations
            
#         Returns:
#             QuerySet: Most experienced doctors
#         """
#         return self.doctors.filter(
#             years_of_experience__gte=min_years,
#             is_available_online=True
#         ).order_by('-years_of_experience', '-rating')[:limit]
    
#     def search_doctors(self, query):
#         """
#         Smart search across doctor name, specialization, qualification, and bio.
        
#         Args:
#             query (str): Search term
            
#         Returns:
#             QuerySet: Matching doctors ordered by rating
#         """
#         return self.doctors.filter(
#             Q(name__icontains=query) |
#             Q(specialization__icontains=query) |
#             Q(qualification__icontains=query) |
#             Q(bio__icontains=query)
#         ).order_by('-rating')
    
#     def get_similar_doctors(self, doctor, limit=4):
#         """
#         Find doctors with same specialization (for "Similar Doctors" section).
        
#         Args:
#             doctor (Doctor): Current doctor object
#             limit (int): Number of similar doctors
            
#         Returns:
#             QuerySet: Similar doctors (same specialty, different doctor)
#         """
#         return self.doctors.filter(
#             specialization=doctor.specialization,
#             is_available_online=True
#         ).exclude(id=doctor.id).order_by('-rating')[:limit]
    
#     def recommend_for_patient(
#         self, 
#         specialization=None, 
#         max_fee=None, 
#         min_rating=3.5,
#         limit=10
#     ):
#         """
#         Personalized recommendations based on patient preferences.
        
#         This is the main recommendation function that combines multiple factors.
        
#         Args:
#             specialization (str): Preferred specialization
#             max_fee (float): Maximum budget
#             min_rating (float): Minimum acceptable rating
#             limit (int): Number of recommendations
            
#         Returns:
#             QuerySet: Recommended doctors prioritized by rating and experience
#         """
#         queryset = self.doctors.filter(
#             is_available_online=True,
#             rating__gte=min_rating
#         )
        
#         # Apply specialization filter
#         if specialization:
#             queryset = queryset.filter(specialization=specialization)
        
#         # Apply price filter
#         if max_fee:
#             queryset = queryset.filter(consultation_fee__lte=max_fee)
        
#         # Order by: rating (descending), experience (descending), fee (ascending)
#         return queryset.order_by(
#             '-rating',
#             '-years_of_experience',
#             'consultation_fee'
#         )[:limit]
    
#     def get_affordable_doctors(self, specialization=None, limit=10):
#         """
#         Get most affordable doctors (sorted by lowest fee).
        
#         Args:
#             specialization (str): Filter by specialization
#             limit (int): Number of recommendations
            
#         Returns:
#             QuerySet: Most affordable doctors with good ratings
#         """
#         queryset = self.doctors.filter(
#             is_available_online=True,
#             rating__gte=3.5  # Minimum acceptable quality
#         )
        
#         if specialization:
#             queryset = queryset.filter(specialization=specialization)
        
#         return queryset.order_by('consultation_fee', '-rating')[:limit]
    
#     def get_premium_doctors(self, specialization=None, limit=10):
#         """
#         Get premium/expert doctors (highest rated, most experienced).
        
#         Args:
#             specialization (str): Filter by specialization
#             limit (int): Number of recommendations
            
#         Returns:
#             QuerySet: Premium doctors with top ratings and experience
#         """
#         queryset = self.doctors.filter(
#             is_available_online=True,
#             rating__gte=4.5,
#             years_of_experience__gte=10
#         )
        
#         if specialization:
#             queryset = queryset.filter(specialization=specialization)
        
#         return queryset.order_by('-rating', '-years_of_experience')[:limit]