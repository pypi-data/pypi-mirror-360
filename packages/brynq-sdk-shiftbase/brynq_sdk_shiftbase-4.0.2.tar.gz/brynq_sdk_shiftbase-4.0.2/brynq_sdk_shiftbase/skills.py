from typing import Dict, Optional, List, Union
import pandas as pd
from .schemas.skills import SkillSchema, SkillGroupSchema
from brynq_sdk_functions import Functions

class Skills:
    """
    Handles all Skills and Skill Groups related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.skill_groups_uri = "skill_groups"
        self.skills_uri = "skills"
        
    def get_skill_groups(self) -> pd.DataFrame:
        """
        Retrieves all skill groups from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/skill_groups
        
        Notes:
            - Minimum plan: premium
        
        Returns:
            pd.DataFrame: Skill groups data
            
        Raises:
            ValueError: If skill groups data fails validation
            requests.HTTPError: 
                - 426: Upgrade required (Premium plan required)
        """
        try:
            # Make the request
            response_data = self.shiftbase.get(self.skill_groups_uri)
            
            if not response_data:
                return pd.DataFrame()
                
            # Extract skill groups from response
            skill_groups = []
            for item in response_data:
                if "SkillGroup" in item:
                    skill_groups.append(item["SkillGroup"])
                    
            # Create DataFrame from response
            df = pd.DataFrame(skill_groups)
            
            # If no data is returned, return an empty DataFrame
            if df.empty:
                return df
                
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, SkillGroupSchema)
                return valid_data
            except Exception as e:
                raise ValueError(f"Invalid skill group data: {str(e)}")
                
        except Exception as e:
            if "426" in str(e):
                raise ValueError("Premium plan required to access skill groups")
            raise
            
    def get_skill_group(self, skill_group_id: str) -> Dict:
        """
        Retrieves a specific skill group by its ID, including its skills.
        
        Endpoint: GET https://api.shiftbase.com/api/skill_groups/{skillGroupId}
        
        Notes:
            - Minimum plan: premium
        
        Args:
            skill_group_id (str): The unique identifier of the skill group
            
        Returns:
            Dict: Skill group details with its skills
            
        Raises:
            ValueError: If skill_group_id is invalid or skill group data fails validation
            requests.HTTPError: 
                - 404: Skill group not found
                - 426: Upgrade required (Premium plan required)
        """
        # Validate skill_group_id
        if not skill_group_id:
            raise ValueError("skill_group_id cannot be empty")
            
        try:
            # Make the request
            response_data = self.shiftbase.get(f"{self.skill_groups_uri}/{skill_group_id}")
            
            if not response_data:
                raise ValueError(f"Skill group with ID {skill_group_id} not found or has an invalid format")
                
            # Validate skill group data
            if "SkillGroup" in response_data:
                skill_group_data = response_data["SkillGroup"]
                df_group = pd.DataFrame([skill_group_data])
                
                try:
                    valid_group_data, _ = Functions.validate_data(df_group, SkillGroupSchema)
                    response_data["SkillGroup"] = valid_group_data.iloc[0].to_dict()
                except Exception as e:
                    raise ValueError(f"Invalid skill group data: {str(e)}")
                
            # Validate skills data
            if "Skill" in response_data and response_data["Skill"]:
                df_skills = pd.DataFrame(response_data["Skill"])
                
                try:
                    valid_skills_data, _ = Functions.validate_data(df_skills, SkillSchema)
                    response_data["Skill"] = valid_skills_data.to_dict('records')
                except Exception as e:
                    raise ValueError(f"Invalid skills data: {str(e)}")
                    
            return pd.DataFrame(response_data)
                
        except Exception as e:
            if "404" in str(e):
                raise ValueError(f"Skill group with ID {skill_group_id} not found")
            if "426" in str(e):
                raise ValueError("Premium plan required to access skill groups")
            raise
            
    def get_skills(self) -> pd.DataFrame:
        """
        Retrieves all skills from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/skills
        
        Notes:
            - Minimum plan: premium
        
        Returns:
            pd.DataFrame: Skills data
            
        Raises:
            ValueError: If skills data fails validation
            requests.HTTPError: 
                - 426: Upgrade required (Premium plan required)
        """
        try:
            # Make the request
            response_data = self.shiftbase.get(self.skills_uri)
            
            if not response_data:
                return pd.DataFrame()
                
            # Extract skills from response
            skills = []
            for item in response_data:
                if "Skill" in item:
                    skills.append(item["Skill"])
                    
            # Create DataFrame from response
            df = pd.DataFrame(skills)
            
            # If no data is returned, return an empty DataFrame
            if df.empty:
                return df
                
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, SkillSchema)
                return valid_data
            except Exception as e:
                raise ValueError(f"Invalid skills data: {str(e)}")
                
        except Exception as e:
            if "426" in str(e):
                raise ValueError("Premium plan required to access skills")
            raise
            
    def get_skill(self, skill_id: str) -> Dict:
        """
        Retrieves a specific skill by its ID.
        
        Endpoint: GET https://api.shiftbase.com/api/skills/{skillId}
        
        Notes:
            - Minimum plan: premium
        
        Args:
            skill_id (str): The unique identifier of the skill
            
        Returns:
            Dict: Skill details
            
        Raises:
            ValueError: If skill_id is invalid or skill data fails validation
            requests.HTTPError: 
                - 404: Skill not found
                - 426: Upgrade required (Premium plan required)
        """
        # Validate skill_id
        if not skill_id:
            raise ValueError("skill_id cannot be empty")
            
        try:
            # Make the request
            response_data = self.shiftbase.get(f"{self.skills_uri}/{skill_id}")
            
            if not response_data:
                raise ValueError(f"Skill with ID {skill_id} not found or has an invalid format")
                
            # Validate skill data
            if "Skill" in response_data:
                skill_data = response_data["Skill"]
                df_skill = pd.DataFrame([skill_data])
                
                try:
                    valid_skill_data, _ = Functions.validate_data(df_skill, SkillSchema)
                    response_data["Skill"] = valid_skill_data.iloc[0].to_dict()
                except Exception as e:
                    raise ValueError(f"Invalid skill data: {str(e)}")
                    
            return response_data
                
        except Exception as e:
            if "404" in str(e):
                raise ValueError(f"Skill with ID {skill_id} not found")
            if "426" in str(e):
                raise ValueError("Premium plan required to access skills")
            raise 