import time
import random

# ==============================================================================
# CASE STUDY ENGINE: Social Proof Generator
# ==============================================================================

class CaseStudyEngine:
    """
    Identifies successful clients and converts their raw data into high-converting
    'Social Proof' assets for marketing automation.
    """
    def __init__(self, business_name, total_revenue, current_health):
        self.business_name = business_name
        self.total_revenue = total_revenue
        self.current_health = current_health

    def compile_case_study_data(self):
        """
        Analyzes the three key 'Win' metrics simulating a query against the Sovereign Vault.
        """
        time.sleep(1) # Simulate pulling historical vault data
        
        # 1. Revenue Growth Tracking
        revenue_str = str(self.total_revenue)
        
        # 2. Review Velocity Shift
        velocities = [
            {"before": 1, "after": 9},
            {"before": 2, "after": 14},
            {"before": 0, "after": 7},
            {"before": 3, "after": 18}
        ]
        v = random.choice(velocities)
        
        # 3. Geo-Grid Transformation
        before_grid = "🟥🟥🟥\n🟥🟧🟥\n🟧🟥🟥" # Day 0 Map
        after_grid = "🟩🟩🟩\n🟩🟩🟧\n🟩🟩🟩"   # Current Live Map
        
        return {
            "business_name": self.business_name,
            "revenue": revenue_str,
            "velocity": v,
            "before_grid": before_grid,
            "after_grid": after_grid
        }

    def generate_html_asset(self, data):
        """
        Builds a clean, shareable image card (rendered here as an HTML block for the Dashboard)
        containing the Before & After map, Total Revenue generated, and Sovereign watermark.
        """
        
        html_card = f"""
        <div style="width: 100%; max-width: 500px; background: #0F172A; border: 2px solid #334155; border-radius: 16px; padding: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); font-family: sans-serif; position: relative; overflow: hidden;">
            
            <!-- Watermark -->
            <div style="position: absolute; top: -15px; right: -25px; background: #3B82F6; color: white; padding: 30px 40px 10px 40px; transform: rotate(45deg); font-size: 0.6em; font-weight: bold; letter-spacing: 1px;">
                VERIFIED BY<br>SOVEREIGN OS
            </div>

            <!-- Header -->
            <h3 style="color: #F8FAFC; margin: 0 0 4px 0; font-size: 1.4em;">{data['business_name']}</h3>
            <p style="color: #38BDF8; margin: 0 0 24px 0; font-weight: 600; font-size: 0.9em;">CASE STUDY</p>
            
            <!-- Revenue Badge -->
            <div style="background: linear-gradient(90deg, #064E3B 0%, #065F46 100%); border: 1px solid #10B981; border-radius: 8px; padding: 16px; text-align: center; margin-bottom: 24px;">
                <p style="color: #A7F3D0; margin: 0 0 4px 0; font-size: 0.8em; text-transform: uppercase;">Attributed Revenue Created</p>
                <h1 style="color: #10B981; margin: 0; font-size: 2.2em; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">{data['revenue']}</h1>
            </div>
            
            <!-- The Map Transformation -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; background: #1E293B; border-radius: 8px; padding: 16px;">
                <div style="text-align: center; flex: 1;">
                    <p style="color: #94A3B8; margin: 0 0 8px 0; font-size: 0.8em;">Day 0 Map</p>
                    <div style="font-family: monospace; font-size: 1.2em; line-height: 1.1; letter-spacing: -2px;">
                        {data['before_grid'].replace(chr(10), '<br>')}
                    </div>
                </div>
                <div style="flex: 0.5; text-align: center;">
                    <span style="font-size: 2em;">➡️</span>
                </div>
                <div style="text-align: center; flex: 1;">
                    <p style="color: #10B981; margin: 0 0 8px 0; font-size: 0.8em; font-weight: bold;">Current Map</p>
                    <div style="font-family: monospace; font-size: 1.2em; line-height: 1.1; letter-spacing: -2px;">
                        {data['after_grid'].replace(chr(10), '<br>')}
                    </div>
                </div>
            </div>
            
            <!-- Review Velocity -->
            <div style="padding-top: 16px; border-top: 1px dashed #334155; display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 1.5em;">⭐</div>
                <div>
                    <h5 style="color: #F8FAFC; margin: 0 0 4px 0;">Review Velocity Shift</h5>
                    <p style="color: #94A3B8; margin: 0; font-size: 0.85em;">
                        Jumped from <b>{data['velocity']['before']} reviews/month</b> to <span style="color: #38BDF8; font-weight: bold;">{data['velocity']['after']} reviews/month</span>.
                    </p>
                </div>
            </div>

        </div>
        """
        return html_card
