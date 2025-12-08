"""
PA Permit Automation System - Main Streamlit Application
Commonwealth of Pennsylvania - AI-Powered Permit Processing
"""
import streamlit as st
from datetime import datetime
import json
from config import Config
from agents import agent_system
from mcp_server import mcp_server
from architecture_diagram import generate_architecture_diagram


# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject CSS immediately after page config - More aggressive to override Streamlit defaults
with st.container():
    st.markdown(
        """
        <style>
        /* Hide sidebar completely */
        section[data-testid="stSidebar"],
        div[data-testid="stSidebar"],
        [data-testid="stSidebar"] {
            display: none !important;
            visibility: hidden !important;
            width: 1px !important;
        }
        
        /* Adjust main content to full width when sidebar is hidden */
        section[data-testid="stAppViewContainer"] > div:first-child,
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        
        /* Hide any empty elements */
        p:empty {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Primary buttons - Force Blue */
        button[kind="primary"],
        button[data-testid="baseButton-primary"],
        .stButton button[kind="primary"],
        .stButton > button[kind="primary"],
        form button[kind="primary"],
        [data-testid="stForm"] button[kind="primary"],
        div[data-testid="stButton"] button[kind="primary"],
        button[data-baseweb="button"][kind="primary"] {
            background-color: #1f77b4 !important;
            background: #1f77b4 !important;
            background-image: none !important;
            color: white !important;
            border: none !important;
            border-color: #1f77b4 !important;
            box-shadow: none !important;
        }
        
        button[kind="primary"]:hover,
        button[kind="primary"]:focus,
        button[kind="primary"]:active,
        button[data-baseweb="button"][kind="primary"]:hover {
            background-color: #1565a0 !important;
            background: #1565a0 !important;
            background-image: none !important;
            border-color: #1565a0 !important;
        }
        
        /* Button text color */
        button[kind="primary"] *,
        button[kind="primary"] span {
            color: white !important;
        }
        
        /* Tab text - White for all */
        button[data-baseweb="tab"] > div,
        button[data-baseweb="tab"] span,
        button[data-baseweb="tab"] p {
            color: white !important;
        }
        
        /* Active tab underline - Blue ONLY */
        button[data-baseweb="tab"][aria-selected="true"],
        div[data-testid="stTabs"] button[aria-selected="true"],
        .stTabs button[aria-selected="true"] {
            border-bottom: 3px solid #1f77b4 !important;
            border-bottom-color: #1f77b4 !important;
            border-bottom-width: 3px !important;
            border-top: none !important;
            border-left: none !important;
            border-right: none !important;
            box-shadow: none !important;
            outline: none !important;
        }
        
        /* Override Streamlit's default red/theme color */
        div[data-testid="stTabs"] > div > div > div > button[aria-selected="true"],
        div[data-testid="stTabs"] button[aria-selected="true"] {
            border-bottom: 3px solid #1f77b4 !important;
            border-bottom-color: #1f77b4 !important;
            background-color: transparent !important;
        }
        
        /* Remove any pseudo-elements that might create red lines */
        button[data-baseweb="tab"][aria-selected="true"]::after,
        button[data-baseweb="tab"][aria-selected="true"]::before,
        div[data-testid="stTabs"] button[aria-selected="true"]::after,
        div[data-testid="stTabs"] button[aria-selected="true"]::before {
            display: none !important;
            content: none !important;
        }
        
        /* Inactive tabs - ensure no underline */
        button[data-baseweb="tab"][aria-selected="false"] {
            border-bottom: none !important;
            border-bottom-width: 0 !important;
        }
    </style>
    <script>
    // Remove any elements showing "0" in the header area
    function removeZeroElements() {
        // Find all elements and check their text content
        const allElements = document.querySelectorAll('*');
        allElements.forEach(el => {
            const text = el.textContent?.trim();
            // If element contains only "0" and is visible, hide it
            if (text === '0' && el.children.length === 0 && el.offsetHeight > 0) {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                el.style.height = '0';
                el.style.width = '0';
            }
        });
        // Also hide any iframes or components in header that might show 0
        document.querySelectorAll('div[data-testid="column"] iframe, div[data-testid="stImage"] iframe').forEach(iframe => {
            if (iframe.title && iframe.title.includes('0')) {
                iframe.style.display = 'none';
            }
        });
    }
    // Run on load and after a short delay to catch dynamic elements
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            removeZeroElements();
            setTimeout(removeZeroElements, 500);
        });
    } else {
        removeZeroElements();
        setTimeout(removeZeroElements, 500);
    }
    </script>
        """,
        unsafe_allow_html=True
    )


def init_session_state():
    """Initialize session state variables"""
    if 'processed_applications' not in st.session_state:
        st.session_state.processed_applications = []
    if 'current_app_id' not in st.session_state:
        st.session_state.current_app_id = None


def main():
    """Main application entry point"""
    init_session_state()
    
    # Header with title - center aligned
    st.markdown("<h2 style='text-align: center;'>AI-Powered Permit Automation System</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top tabs navigation
    tab1, tab2, tab3 = st.tabs([" Submit Application", " Application Status", " System Architecture"])
    
    # Tab content
    with tab1:
        show_application_page()
    
    with tab2:
        show_status_page()
    
    with tab3:
        show_architecture_page()


def show_application_page():
    """Display permit application submission page"""
    st.subheader(" Submit New Permit Application")
    st.markdown("**Demo Mode:** Select a company scenario and click Submit to see the AI agents in action!")
    
    st.markdown("---")
    
    # Company selector outside the form to make it reactive
    col1, col2 = st.columns(2)
    
    with col1:
        # Company selector integrated into Applicant Name field
        company_choice = st.selectbox(
            "Applicant Name / Organization *",
            ["🟢 Acme Environmental Solutions Corp ", "🔴 QuickFix Inc ", "⭐ Perfect Environmental Corp "],
            help="Select a company to see how AI agents handle different application quality levels"
        )
    
    # Store company choice in session state for form reactivity
    if 'selected_company' not in st.session_state or st.session_state.selected_company != company_choice:
        st.session_state.selected_company = company_choice
        st.session_state.form_data = {}
        st.rerun()  # Refresh the page to update form fields
    
    # Set default values based on company choice
    is_good_company = "Acme" in company_choice
    is_perfect_company = "Perfect" in company_choice
    
    if is_perfect_company:
        # PERFECT - Flawless application that will be FULLY APPROVED
                applicant_name = company_choice  # Use the selected company name
                location_default = "456 Clean Water Drive, Harrisburg, Dauphin County, PA 17120 (GPS: 40.2737° N, 76.8844° W). Site ID: DEP-DAU-2024-PERFECT-001"
                email_default = "permits@perfect-environmental.com | 24/7 Emergency Hotline: (717) 555-0100 | Compliance Officer: Sarah Johnson, PE #PE-789012"
                project_name_default = "Susquehanna River State-of-the-Art Water Treatment Facility - Zero Impact Design"
                cost_default = 5000000
                duration_default = 24
                description_default = "Revolutionary zero-impact water treatment facility utilizing cutting-edge technology to achieve 100% environmental compliance. EQUIPMENT SPECIFICATIONS: (1) Advanced reverse osmosis system - Dow Filmtec XLE-440 membranes, 100 MGD capacity, NSF/ANSI 58 certified with 99.9% contaminant removal (2) Solar-powered UV sterilization - Trojan UVSwift SC-8 system, 100 MGD rated, NSF/ANSI 55 Class A certified with backup battery system (3) AI-powered SCADA monitoring - Siemens SIMATIC PCS 7 with predictive maintenance, real-time water quality sensors, automated compliance reporting (4) Zero-waste discharge system - Advanced oxidation process with complete contaminant destruction (5) Renewable energy integration - 2MW solar array with Tesla Powerpack storage. CONSTRUCTION TIMELINE: Phase 1 (Months 1-8): Site preparation, renewable energy installation, foundation work. Phase 2 (Months 9-16): Equipment installation, system integration, testing. Phase 3 (Months 17-24): Commissioning, staff training, performance optimization. SAFETY: OSHA VPP Star certified contractors, daily safety audits, comprehensive confined space protocols, emergency response drills. EMERGENCY RESPONSE: On-site 24/7 certified operators, redundant backup systems, immediate PA DEP notification system, community emergency communication plan. All work exceeds PA DEP Chapter 109 Safe Drinking Water regulations with 200% safety margins."
                environmental_default = "ENVIRONMENTAL IMPACT ASSESSMENT: EXCEPTIONAL POSITIVE IMPACTS: (1) 100% elimination of pollutant discharge to Susquehanna River (2) 99.99% removal of all pathogens including Cryptosporidium, Giardia, and viruses (3) 50% energy efficiency improvement through renewable integration (4) Net positive environmental impact - facility produces clean energy surplus (5) Enhanced water quality for 1,000,000+ downstream residents (6) Zero carbon footprint operation (7) Habitat restoration - 50 acres of wetlands created. MITIGATION MEASURES: (1) All construction within designated industrial zone - zero new land disturbance (2) Advanced noise control - Work limited to 8am-6pm, 40dB sound barriers, vibration dampening (3) Comprehensive dust control - Automated water misting, enclosed material storage, HEPA filtration (4) Superior erosion control - Geotextile barriers, bio-retention systems, stormwater treatment (5) Continuous water quality monitoring - Real-time upstream/downstream sampling, automated alerts (6) Wildlife protection - Migratory bird monitoring, fish passage improvements (7) Community engagement - Monthly public meetings, educational programs. REGULATORY COMPLIANCE: Exceeds all PA DEP Title 25 Chapter 93 Water Quality Standards, EPA Safe Drinking Water Act 42 USC 300f, Clean Water Act Section 402 NPDES permit requirements. Third-party environmental audit completed by GreenTech Solutions (Report #GT-2024-PERFECT-001, attached). PA Fish and Boat Commission consultation completed with habitat enhancement recommendations implemented. EPA Region 3 pre-approval consultation completed. LEED Platinum certification pending."
    elif is_good_company:
        # ACME - Complete application that will be APPROVED
        applicant_name = company_choice  # Use the selected company name
        location_default = "123 River Avenue, Pittsburgh, Allegheny County, PA 15222 (GPS: 40.4406° N, 79.9959° W). Site ID: DEP-ALGH-2024-001"
        email_default = "permits@acme-environmental.com | 24/7 Emergency Hotline: (412) 555-0199"
        project_name_default = "Monongahela River Advanced Water Treatment Facility Upgrade - Phase 3"
        cost_default = 2500000
        duration_default = 18
        description_default = "Comprehensive upgrade to the existing Monongahela River water treatment facility to enhance water quality and increase treatment capacity by 30%. EQUIPMENT SPECIFICATIONS: (1) Advanced membrane filtration - Pall Corporation Aria Series AP-10 ultrafiltration modules, 50 MGD capacity, NSF/ANSI 61 certified (2) UV disinfection - Trojan UVSwift SC-4 system, 50 MGD rated, NSF/ANSI 55 Class A certified (3) Automated SCADA monitoring - Hach Claros Water Intelligence System with real-time turbidity, pH, chlorine sensors. CONSTRUCTION TIMELINE: Phase 1 (Months 1-6): Site prep, foundation work, equipment delivery. Phase 2 (Months 7-12): Installation, piping, electrical integration, system testing. Phase 3 (Months 13-18): Commissioning, operator training, performance validation. SAFETY: OSHA-certified contractors, daily safety briefings, confined space entry protocols. EMERGENCY RESPONSE: On-site 24/7 emergency response team, backup water supply from Allegheny Reservoir, emergency notification system to PA DEP within 1 hour of any incident. All work complies with PA DEP Chapter 109 Safe Drinking Water regulations."
        environmental_default = "ENVIRONMENTAL IMPACT ASSESSMENT: POSITIVE IMPACTS: (1) 40% reduction in pollutant discharge to Monongahela River (2) Removal of 99.9% of Cryptosporidium and Giardia (3) 25% energy efficiency improvement through variable frequency drives (4) Enhanced water quality for 500,000+ downstream residents. MITIGATION MEASURES: (1) All construction within existing facility footprint - no new land disturbance (2) Noise control: Work limited to 7am-7pm, sound barriers around equipment (3) Dust control: Water spraying, covered material storage (4) Erosion control: Silt fencing, straw bales, stormwater retention (5) Water quality monitoring: Daily upstream/downstream sampling during construction. REGULATORY COMPLIANCE: Fully compliant with PA DEP Title 25 Chapter 93 Water Quality Standards, EPA Safe Drinking Water Act 42 USC 300f, Clean Water Act Section 402 NPDES permit requirements. Third-party environmental audit completed by EcoConsult Solutions (Report #EC-2024-089, attached). PA Fish and Boat Commission consultation completed - no impact to critical habitat."
    else:
        # QUICKFIX - Incomplete/problematic application that will be REJECTED
        applicant_name = company_choice  # Use the selected company name
        location_default = "Pittsburgh"
        email_default = "quick@fix.com"
        project_name_default = "Water stuff"
        cost_default = 10000
        duration_default = 1
        description_default = "Need to fix water. Will add some stuff."
        environmental_default = "Should be ok."
        
    # Now create the form with reactive fields
    with st.form("permit_application_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Applicant name is now handled by the dropdown above
            
            permit_type = st.selectbox(
                "Permit Type *",
                Config.PERMIT_TYPES,
                index=1,  # Default to "Environmental Permit - Water Quality"
                help="Select the type of permit you are applying for"
            )
            
            location = st.text_input(
                "Project Location *",
                value=location_default,
                placeholder="City, County, PA"
            )
            
            contact_email = st.text_input(
                "Contact Email *",
                value=email_default,
                placeholder="applicant@example.com"
            )
        
        with col2:
            project_name = st.text_input(
                "Project Name *",
                value=project_name_default,
                placeholder="Enter project name"
            )
            
            estimated_cost = st.number_input(
                "Estimated Project Cost ($)",
                min_value=0,
                value=cost_default,
                step=1000,
                help="Total estimated cost of the project"
            )
            
            start_date = st.date_input(
                "Proposed Start Date",
                help="When do you plan to start this project?"
            )
            
            duration_months = st.number_input(
                "Project Duration (months)",
                min_value=1,
                max_value=120,
                value=duration_default
            )
        
        project_description = st.text_area(
            "Project Description *",
            value=description_default,
            placeholder="Provide detailed description of the project, activities, and objectives...",
            height=150,
            help="Include all relevant details about the project"
        )
        
        environmental_impact = st.text_area(
            "Environmental Impact Assessment",
            value=environmental_default,
            placeholder="Describe potential environmental impacts and mitigation measures...",
            height=100
        )
        
        st.markdown("---")
        
        col_btn1, col_btn2 = st.columns([3, 1])
        
        with col_btn2:
            submitted = st.form_submit_button(
                " Submit Application",
                use_container_width=True,
                type="primary",
                key="submit_application_btn"
            )
        
        # Handle form submission
        if submitted:
            # Validate required fields
            if not all([applicant_name, permit_type, location, contact_email, 
                       project_name, project_description]):
                st.error("❌ Please fill in all required fields marked with *")
                return
            
            # Create application data
            application_data = {
                "applicant_name": applicant_name,
                "permit_type": permit_type,
                "location": location,
                "contact_email": contact_email,
                "project_name": project_name,
                "estimated_cost": estimated_cost,
                "start_date": str(start_date),
                "duration_months": duration_months,
                "project_description": project_description,
                "environmental_impact": environmental_impact,
                "submission_date": datetime.now().isoformat()
            }
            
            # Process application with AI agents
            st.markdown("---")
            st.markdown("### AI Agent Workflow - Live Processing")
            
            # Create a container for live agent updates
            agent_container = st.container()
        
            with agent_container:
                # Create columns for visual workflow WITH OUTPUT AREAS
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    stage1_icon = st.empty()
                    stage1_status = st.empty()
                    stage1_icon.markdown("### 🔵")
                    stage1_status.markdown("**Intake Agent**\n\n⏳ Waiting...")
                    st.markdown("---")
                    stage1_output = st.empty()
            
                with col2:
                    stage2_icon = st.empty()
                    stage2_status = st.empty()
                    stage2_icon.markdown("### ⚪")
                    stage2_status.markdown("**Review Agent**\n\n⏳ Waiting...")
                    st.markdown("---")
                    stage2_output = st.empty()
            
                with col3:
                    stage3_icon = st.empty()
                    stage3_status = st.empty()
                    stage3_icon.markdown("### ⚪")
                    stage3_status.markdown("**Compliance Agent**\n\n⏳ Waiting...")
                    st.markdown("---")
                    stage3_output = st.empty()
            
                with col4:
                    stage4_icon = st.empty()
                    stage4_status = st.empty()
                    stage4_icon.markdown("### ⚪")
                    stage4_status.markdown("**Decision Agent**\n\n⏳ Waiting...")
                    st.markdown("---")
                    stage4_output = st.empty()
        
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            import time
            
            # Initialize application in MCP
            application_id = f"PA-{application_data.get('permit_type', 'UNKNOWN')}-{id(application_data)}"
            mcp_server.create_context(application_id, application_data)
            
            result = {
                "application_id": application_id,
                "stages": {},
                "final_decision": None
            }
            
            # Stage 1: Intake
            stage1_icon.markdown("### 🟡")
            stage1_status.markdown("**Intake Agent**\n\n Processing...")
            status_text.markdown("**Stage 1/4:** Intake Agent validating application completeness...")
            progress_bar.progress(10)
            
            try:
                intake_result = agent_system._intake_stage(application_id, application_data)
                result["stages"]["intake"] = intake_result
                
                stage1_icon.markdown("### 🟢")
                stage1_status.markdown("**Intake Agent**\n\n✅ Complete!")
                progress_bar.progress(25)
                
                # Display intake results in column
                with stage1_output.container():
                    if intake_result.get("complete"):
                        st.success("✅ COMPLETE")
                    else:
                        st.error("❌ INCOMPLETE")
                    with st.expander("📋 Details", expanded=True):
                        st.caption(intake_result.get("notes", "")[:300] + "..." if len(intake_result.get("notes", "")) > 300 else intake_result.get("notes", ""))
                
                # Check if application is complete - if not, stop processing
                if not intake_result.get("complete", False):
                    result["final_decision"] = "INCOMPLETE - Additional information required"
                
                    # Update other agents to show they didn't run
                    stage2_icon.markdown("### ⚪")
                    stage2_status.markdown("**Review Agent**\n\n⏸️ Skipped")

                    stage3_icon.markdown("### ⚪")
                    stage3_status.markdown("**Compliance Agent**\n\n⏸️ Skipped")

                    stage4_icon.markdown("### ⚪")
                    stage4_status.markdown("**Decision Agent**\n\n⏸️ Skipped")

                    progress_bar.progress(25)
                    status_text.markdown("**❌ Processing stopped - Application incomplete**")

                    # Update final state
                    mcp_server.set_application_state(
                        application_id, 
                        stage="stopped", 
                        status=result["final_decision"],
                        agent="intake"
                    )
                else:
                    # Continue with full processing for complete applications
                    # A2A Handoff to Review
                    handoff_1 = mcp_server.a2a_handoff(
                        application_id=application_id,
                        from_agent="intake",
                        to_agent="review",
                        context_update={"intake_complete": True, "intake_notes": intake_result.get("notes")}
                    )
                
                # Stage 2: Review
                stage2_icon.markdown("### 🟡")
                stage2_status.markdown("**Review Agent**\n\n Processing...")
                status_text.markdown("**Stage 2/4:** Review Agent conducting technical analysis...")
                progress_bar.progress(40)
                
                review_result = agent_system._review_stage(application_id, handoff_1["context"])
                result["stages"]["review"] = review_result
                
                stage2_icon.markdown("### 🟢")
                stage2_status.markdown("**Review Agent**\n\n✅ Complete!")
                progress_bar.progress(50)
                
                # Display review results in column
                with stage2_output.container():
                    if review_result.get("has_concerns"):
                        st.warning("⚠️ CONCERNS")
                    else:
                        st.success("✅ APPROVED")
                    with st.expander("📋 Details", expanded=True):
                        st.caption(review_result.get("findings", "")[:300] + "..." if len(review_result.get("findings", "")) > 300 else review_result.get("findings", ""))
                
                # A2A Handoff to Compliance
                handoff_2 = mcp_server.a2a_handoff(
                    application_id=application_id,
                    from_agent="review",
                    to_agent="compliance",
                    context_update={"review_complete": True, "review_findings": review_result.get("findings")}
                )
                
                # Stage 3: Compliance
                stage3_icon.markdown("### 🟡")
                stage3_status.markdown("**Compliance Agent**\n\n🔄 Processing...")
                status_text.markdown("**Stage 3/4:** Compliance Agent verifying regulations...")
                progress_bar.progress(65)
                
                compliance_result = agent_system._compliance_stage(application_id, handoff_2["context"])
                result["stages"]["compliance"] = compliance_result
                
                stage3_icon.markdown("### 🟢")
                stage3_status.markdown("**Compliance Agent**\n\n✅ Complete!")
                progress_bar.progress(75)
                
                # Display compliance results in column
                with stage3_output.container():
                    comp_status = compliance_result.get("status", "UNKNOWN")
                    if comp_status == "COMPLIANT":
                        st.success(f"✅ {comp_status}")
                    elif comp_status == "CONDITIONAL":
                        st.warning(f"⚠️ {comp_status}")
                    else:
                        st.error(f"❌ {comp_status}")
                    with st.expander("📋 Details", expanded=True):
                        st.caption(compliance_result.get("report", "")[:300] + "..." if len(compliance_result.get("report", "")) > 300 else compliance_result.get("report", ""))
                
                # A2A Handoff to Decision
                handoff_3 = mcp_server.a2a_handoff(
                    application_id=application_id,
                    from_agent="compliance",
                    to_agent="decision",
                    context_update={
                        "compliance_complete": True, 
                        "compliance_status": compliance_result.get("status")
                    }
                )
                
                # Stage 4: Decision
                stage4_icon.markdown("### 🟡")
                stage4_status.markdown("**Decision Agent**\n\n🔄 Processing...")
                status_text.markdown("**Stage 4/4:** Decision Agent making final determination...")
                progress_bar.progress(90)
                
                decision_result = agent_system._decision_stage(application_id, handoff_3["context"])
                result["stages"]["decision"] = decision_result
                result["final_decision"] = decision_result.get("decision")
                
                stage4_icon.markdown("### 🟢")
                stage4_status.markdown("**Decision Agent**\n\n Complete!")
                progress_bar.progress(100)
                status_text.markdown("**✅ All agents completed processing!**")
                
                # Display decision results in column
                with stage4_output.container():
                    decision = decision_result.get("decision", "UNKNOWN")
                    if "APPROVED" in decision:
                        st.success(f"✅ {decision}")
                    elif "DENIED" in decision:
                        st.error(f"❌ {decision}")
                    else:
                        st.info(f"ℹ {decision}")
                    with st.expander("📋 Details", expanded=True):
                        st.caption(decision_result.get("rationale", "")[:300] + "..." if len(decision_result.get("rationale", "")) > 300 else decision_result.get("rationale", ""))
                
                # Update final state
                mcp_server.set_application_state(
                    application_id, 
                    stage="completed", 
                    status=result["final_decision"],
                    agent="decision"
                )
            
                # Store result
                st.session_state.processed_applications.append({
                    "timestamp": datetime.now(),
                    "application_data": application_data,
                    "result": result
                })
                st.session_state.current_app_id = result["application_id"]
                
                # Small delay to show completion
                time.sleep(1)
            
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
            
                st.markdown("---")
                st.markdown("###  Final Summary")
                
                # Display results
                st.success(f"✅ Application processed successfully!")
                st.info(f"**Application ID:** {result['application_id']}")
                
                # Show final decision
                decision = result.get("final_decision", "Unknown")
                if "APPROVED" in decision:
                    st.success(f"### ✅ Final Decision: {decision}")
                elif "DENIED" in decision:
                    st.error(f"### ❌ Final Decision: {decision}")
                elif "INCOMPLETE" in decision or "MORE INFORMATION" in decision:
                    st.warning(f"### ⚠️ Final Decision: {decision}")
                else:
                    st.info(f"### ℹ Final Decision: {decision}")
                
                # Get application history from MCP
                history = mcp_server.get_application_history(result["application_id"])
                if history:
                    with st.expander(" View Agent Handoff History (A2A)"):
                        for i, record in enumerate(history, 1):
                            st.markdown(f"**Handoff {i}:** {record['from_agent']} → {record['to_agent']}")
                            st.caption(f"Time: {record['timestamp']}")
                            st.json(record['context_update'])
            
            except Exception as e:
                st.error(f"❌ Error processing application: {str(e)}")
                st.exception(e)


def show_status_page():
    """Display application status and history page"""
    st.subheader(" Application Status & History")
    
    if not st.session_state.processed_applications:
        st.info("ℹ No applications have been processed yet. Submit an application to get started.")
        return
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_apps = len(st.session_state.processed_applications)
    approved = sum(1 for app in st.session_state.processed_applications 
                  if "APPROVED" in app["result"].get("final_decision", ""))
    denied = sum(1 for app in st.session_state.processed_applications 
                if "DENIED" in app["result"].get("final_decision", ""))
    pending = total_apps - approved - denied
    
    col1.metric("Total Applications", total_apps)
    col2.metric("Approved", approved, delta=f"{(approved/total_apps*100):.1f}%")
    col3.metric("Denied", denied, delta=f"{(denied/total_apps*100):.1f}%")
    col4.metric("Other", pending)
    
    st.markdown("---")
    
    # Application list
    st.markdown("### Recent Applications")
    
    for i, app in enumerate(reversed(st.session_state.processed_applications)):
        with st.expander(
            f"**{app['application_data']['project_name']}** - "
            f"{app['application_data']['permit_type']} - "
            f"{app['timestamp'].strftime('%Y-%m-%d %H:%M')}"
        ):
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("#### Application Details")
                st.markdown(f"**Applicant:** {app['application_data']['applicant_name']}")
                st.markdown(f"**Location:** {app['application_data']['location']}")
                st.markdown(f"**Cost:** ${app['application_data']['estimated_cost']:,}")
                st.markdown(f"**Duration:** {app['application_data']['duration_months']} months")
            
            with col_b:
                st.markdown("#### Processing Result")
                st.markdown(f"**Application ID:** {app['result']['application_id']}")
                decision = app['result'].get('final_decision', 'Unknown')
                
                if "APPROVED" in decision:
                    st.success(f"**Decision:** {decision}")
                elif "DENIED" in decision:
                    st.error(f"**Decision:** {decision}")
                else:
                    st.warning(f"**Decision:** {decision}")
            
            st.markdown("#### Project Description")
            st.write(app['application_data']['project_description'])
            
            # Show stage details
            st.markdown("#### Processing Stages")
            stage_tabs = st.tabs(list(app['result']['stages'].keys()))
            
            for tab, (stage_name, stage_data) in zip(stage_tabs, app['result']['stages'].items()):
                with tab:
                    st.json(stage_data)
    
    # Export functionality
    st.markdown("---")
    if st.button(" Export All Applications to JSON"):
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_applications": len(st.session_state.processed_applications),
            "applications": [
                {
                    "timestamp": app["timestamp"].isoformat(),
                    "data": app["application_data"],
                    "result": app["result"]
                }
                for app in st.session_state.processed_applications
            ]
        }
        
        st.download_button(
            label="Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"pa_permits_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def show_architecture_page():
    """Display system architecture diagram and documentation"""
    st.subheader(" System Architecture")
    st.markdown("Complete visual representation of the PA Permit Automation System")
    
    # Tabs for different views
    arch_tab1, arch_tab2 = st.tabs([" Full System Architecture", " Agent Workflow"])
    
    with arch_tab1:
        st.markdown("### Complete System Overview")
        st.markdown("This diagram shows all components and their interactions:")
        diagram = generate_architecture_diagram()
        _ = st.graphviz_chart(diagram, use_container_width=True)  # Suppress return value
    
    with arch_tab2:
        st.markdown("### Agent Workflow - Processing Pipeline")
        st.markdown("This shows how agents process a permit application step-by-step:")
        
        # Generate and display workflow diagram
        from architecture_diagram import generate_workflow_diagram
        workflow_diagram = generate_workflow_diagram()
        
        _ = st.graphviz_chart(workflow_diagram, use_container_width=True)  # Suppress return value
        
        st.markdown("---")
        st.markdown("#### Live Example:")
        st.markdown("""
        When you submit an application on the **Submit Application** tab, you'll see:
        
        1. **🔵 Intake Agent** - Starts first, validates completeness
        2. **🟡 Processing** - Yellow circle shows active agent
        3. **🟢 Complete** - Green circle shows completed stage
        4. **A2A Handoff** - Context automatically transfers to next agent
        5. **Final Decision** - Decision Agent provides final determination
        
        All agent interactions are logged in the MCP Server for full auditability.
        """)
    
    st.markdown("---")
    
    # Architecture explanation
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("###  Core Components")
        st.markdown("""
        **1. Streamlit UI Layer**
        - User interface for application submission
        - Real-time status tracking
        - Interactive dashboards
        
        **2. AI Agent System (CrewAI)**
        - Intake Specialist Agent
        - Technical Review Agent
        - Compliance Verification Agent
        - Decision Authority Agent
        
        **3. MCP Server**
        - Context management
        - State persistence
        - Agent coordination
        
        **4. Ollama LLM**
        - Natural language processing
        - Decision reasoning
        - Report generation
        """)
    
    with col2:
        st.markdown("###  Workflow Process")
        st.markdown("""
        **Stage 1: Intake**
        - Validate application completeness
        - Check required fields
        - Initial assessment
        
        **Stage 2: Technical Review**
        - Analyze technical feasibility
        - Assess environmental impact
        - Identify risks
        
        **Stage 3: Compliance**
        - Verify regulatory compliance
        - Check PA DEP requirements
        - Validate federal regulations
        
        **Stage 4: Decision**
        - Synthesize all reviews
        - Make final determination
        - Generate decision rationale
        """)
    
    st.markdown("---")
    
    # Technology stack
    st.markdown("###  Technology Stack")
    
    tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)
    
    with tech_col1:
        st.markdown("**Frontend**")
        st.markdown("- Streamlit")
        st.markdown("- Python 3.11")
        st.markdown("- Graphviz")
    
    with tech_col2:
        st.markdown("**AI Framework**")
        st.markdown("- CrewAI")
        st.markdown("- Ollama")
        st.markdown("- Mixtral Model")
    
    with tech_col3:
        st.markdown("**Backend**")
        st.markdown("- MCP Server")
        st.markdown("- A2A Handoff")
        st.markdown("- Context Manager")
    
    with tech_col4:
        st.markdown("**Data**")
        st.markdown("- JSON Storage")
        st.markdown("- Session State")
        st.markdown("- Real-time Sync")
    
    st.markdown("---")
    
    # A2A Handoff explanation
    with st.expander(" Understanding Agent-to-Agent (A2A) Handoff"):
        st.markdown("""
        ### Agent-to-Agent (A2A) Handoff Pattern
        
        The A2A handoff pattern enables seamless context transfer between specialized agents:
        
        **How it Works:**
        1. **Context Preservation**: Each agent's findings are stored in MCP server
        2. **Handoff Initiation**: Current agent completes its task and triggers handoff
        3. **Context Transfer**: MCP server transfers relevant context to next agent
        4. **State Management**: Application state is updated to reflect current stage
        5. **History Tracking**: All handoffs are logged for audit trail
        
        **Benefits:**
        - ✅ Maintains context across agent transitions
        - ✅ Enables specialized expertise per stage
        - ✅ Provides complete audit trail
        - ✅ Allows parallel processing capabilities
        - ✅ Ensures data consistency
        
        **Example Flow:**
        ```
        Intake Agent (validates) 
            → A2A Handoff → 
        Review Agent (analyzes) 
            → A2A Handoff → 
        Compliance Agent (verifies) 
            → A2A Handoff → 
        Decision Agent (approves/denies)
        ```
        """)


if __name__ == "__main__":
    main()

