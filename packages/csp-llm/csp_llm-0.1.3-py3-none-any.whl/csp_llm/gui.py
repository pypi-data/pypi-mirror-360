import asyncio

import constants
import streamlit as st
from annotated_types import T
from constants import QUICK_EXAMPLE_PROBLEMS
from csp_tools import CSPExtractor, CSPGenerator, MCPCSPRunner
from streamlit_ace import st_ace


def initialize_components():

    # Initialize components
    if "code_generator" not in st.session_state:
        st.session_state.code_generator = CSPGenerator(
            st.session_state.model, st.session_state.brand
        )
    if len(st.session_state.code_generator.get_error_messages()) != 0:
        for msg in st.session_state.code_generator.get_error_messages():
            st.warning(msg)
        return

    if "mcp_runner" not in st.session_state:
        st.session_state.mcp_runner = MCPCSPRunner()

    if "extractor" not in st.session_state:
        st.session_state.extractor = CSPExtractor()

    if "problem_value" not in st.session_state:
        st.session_state.problem_value = ""

    # Variables pour détecter les changements
    if "last_selection" not in st.session_state:
        st.session_state.last_selection = ""
    if "last_uploaded_file" not in st.session_state:
        st.session_state.last_uploaded_file = None
    if "problem_label" not in st.session_state:
        st.session_state.problem_label = ""
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 2000


def handle_model_selection() -> None:
    selected_model = st.session_state["model_key"]
    parse_split = selected_model.split("[")
    model = parse_split[1].replace("]", "").strip()
    brand = parse_split[0].strip()
    st.session_state.code_generator = CSPGenerator(model, brand)


def main():

    st.set_page_config(
        page_title="CSP Problem Solver with LLM", page_icon="💻", layout="wide"
    )
    st.title("💻 Constraint Programming with LLM")
    st.markdown("Solve constraint programming problems using LLM")

    st.sidebar.header("⚙️ Configuration")

    st.sidebar.subheader("🎛️ Model parameters")

    model = st.sidebar.selectbox(
        "Model",
        constants.MODELS,
        index=0,
        key="model_key",
        on_change=handle_model_selection,
    )
    parse_split = model.split("[")
    st.session_state.model = parse_split[1].replace("]", "").strip()
    st.session_state.brand = parse_split[0].strip()

    st.sidebar.divider()

    initialize_components()

    temperature = st.sidebar.slider(
        "Temperature",
        0.0,
        2.0,
        st.session_state.temperature,
        0.1,
        help="Controls creativity (0 = deterministic, 2 = very creative)",
    )
    st.session_state.temperature = temperature

    max_tokens = st.sidebar.slider(
        "Max Tokens",
        1000,
        5000,
        st.session_state.max_tokens,
        100,
        help="Maximum number of tokens in the response",
    )
    st.session_state.max_tokens = max_tokens
    st.sidebar.divider()
    st.empty()
    st.empty()
    st.empty()

    st.sidebar.link_button(
        "🚨 Report an issue",
        "mailto:kemgue@cril.fr?subject=Report an issue in csp llm app",
    )

    st.divider()

    st.subheader(
        f"Selected model is {st.session_state.model} from {st.session_state.brand} provider"
    )

    # Main interface
    col1, col2 = st.columns([1, 1])

    with col1:
        selected_example = st.selectbox(
            "Choose an example or custom:",
            list(constants.EXAMPLE_PROBLEMS.keys()),
            index=0,
            key="problem_selector",
            help="Select an problem example",
        )

        uploaded_txt_file = st.file_uploader(
            "Choose a problem file",
            type=["txt", "md"],
            key="file_uploader",
            help="Upload a problem description from a file",
        )

        # select and upload logic

        content_updated = False

        # Is new selection done ?
        if selected_example != st.session_state.last_selection:
            if selected_example != "Custom":
                st.session_state.problem_value = constants.EXAMPLE_PROBLEMS[
                    selected_example
                ]

                st.session_state.problem_label = "Problem Description:"
                content_updated = True
            else:
                st.session_state.problem_value = ""
                st.session_state.problem_label = (
                    "Describe your constraint programming problem:"
                )
                content_updated = True

            st.session_state.last_selection = selected_example

        # Is new file uploaded ?
        elif (
            uploaded_txt_file is not None
            and uploaded_txt_file != st.session_state.last_uploaded_file
        ):
            try:
                file_content = uploaded_txt_file.read().decode("utf-8")
                st.session_state.problem_value = file_content
                content_updated = True
                st.session_state.problem_label = f"A constraint programming problem from file {uploaded_txt_file.name}"

                # not necessary
                # uploaded_txt_file.seek(0)

            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

            st.session_state.last_uploaded_file = uploaded_txt_file

        # ===================

        st.header("Problem Description")
        tab1, tab2 = st.tabs(["📝 Problem description", "📖 Preview Markdown"])

        with tab1:
            problem_description = st.text_area(
                st.session_state.problem_label,
                value=st.session_state.problem_value,
                height=160,
                placeholder="Example: Place 4 queens on a 4x4 chessboard...",
                key="problem_key",
            )

        with tab2:
            st.markdown("**Preview Markdown:**")
            st.markdown(problem_description)

        if st.button("🤖 Generate CSP Code with LLM", type="primary"):
            if problem_description:
                # Streaming mode with proper async handling
                st.markdown("### 🔄 LLM is generating code...")
                streaming_container = st.container()

                async def run_streaming_generation():
                    return await st.session_state.code_generator.generate_csp_code_stream_async(
                        problem_description, streaming_container
                    )

                # Execute the async streaming function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    with st.spinner("LLM is generating..."):
                        llm_response = loop.run_until_complete(
                            run_streaming_generation()
                        )

                    # Extract PyCSP3 code
                    extracted_code = st.session_state.extractor.extract_pycsp3_code(
                        llm_response
                    )

                    # Store in session state
                    st.session_state.generated_code = extracted_code
                    st.session_state.llm_response = llm_response

                    st.success("✅ Code generated successfully!")
                except Exception as e:
                    st.error(f"❌ Generation failed: {str(e)}")
                finally:
                    loop.close()

            else:
                st.error("Please enter a problem description.")

    with col2:
        st.header("Generated PyCSP3 Code")

        if "generated_code" in st.session_state:
            # Show final generated code in a clean format
            st.subheader("📋 Final Generated Code")
            # st.code(st.session_state.generated_code, language="python")
            theme_editor = st.selectbox(
                "🎨 Thème:",
                [
                    "twilight",
                    "terminal",
                    "dracula",
                    "tomorrow",
                    "xcode",
                    "solarized_dark",
                    "vibrant_ink",
                ],
                index=0,
            )

            code = st_ace(
                value=st.session_state.generated_code,
                language="python",
                theme=theme_editor,
                show_gutter=True,  # Affiche les numéros de ligne
                show_print_margin=True,
                wrap=False,
                font_size=14,
                height=400,
                readonly=True,
            )

            # Show raw LLM response in expander
            with st.expander("🤖 View Full LLM Response"):
                st.text(st.session_state.llm_response)

            # Edit code option
            if st.checkbox("✏️ Edit code before execution"):
                edited_code = st_ace(
                    value=st.session_state.generated_code,
                    language="python",
                    theme=theme_editor,
                    key="code_editor",
                    height=400,
                    font_size=14,
                    auto_update=True,
                    annotations=None,
                    markers=None,
                )
                execution_code = edited_code
                execution_code = edited_code
            else:
                execution_code = st.session_state.generated_code

            # Execution controls
            st.subheader("🚀 Execution Controls")

            col2_1, col2_2, col2_3 = st.columns([1, 1, 1])

            with col2_1:
                if st.button("🔧 Execute via MCP", type="secondary"):
                    with st.spinner("Executing CSP code via MCP..."):
                        # Create real-time execution container
                        execution_container = st.container()
                        execution_status = execution_container.empty()
                        execution_progress = execution_container.progress(0)

                        # Update progress
                        execution_status.info("🔄 Initializing MCP runner...")
                        execution_progress.progress(25)

                        # Run code through MCP
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        try:
                            # Initialize MCP if needed
                            execution_status.info("🔄 Setting up MCP session...")
                            execution_progress.progress(50)

                            if (
                                not hasattr(st.session_state.mcp_runner, "session")
                                or not st.session_state.mcp_runner.session
                            ):
                                loop.run_until_complete(
                                    st.session_state.mcp_runner.initialize_mcp()
                                )

                            # Execute code
                            execution_status.info("🔄 Executing CSP code...")
                            execution_progress.progress(75)

                            result = loop.run_until_complete(
                                st.session_state.mcp_runner.run_csp_code(execution_code)
                            )

                            execution_progress.progress(100)
                            execution_status.success("✅ Execution completed!")

                            st.session_state.execution_result = result

                        except Exception as e:
                            execution_status.error(f"❌ Execution failed: {str(e)}")
                            st.session_state.execution_result = {
                                "success": False,
                                "output": "",
                                "error": str(e),
                                "code": execution_code,
                            }
                        finally:
                            loop.close()

            with col2_2:
                if st.button("💾 Save Code"):
                    # Create download link for the code
                    st.download_button(
                        label="📥 Download PyCSP3 Code",
                        data=execution_code,
                        file_name=f"csp_problem_{len(execution_code)}.py",
                        mime="text/plain",
                    )

            with col2_3:
                if st.button("🔄 Reset"):
                    # Clear session state
                    for key in [
                        "generated_code",
                        "llm_response",
                        "execution_result",
                    ]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

        else:
            st.info("💡 Tips to use:")
            st.info(
                "👈 The description of a problem for which you want to generate code in PyCSP3 is in natural language\n\n"
                "👈 On the left, you can select on the left, an example problem or select **custom** to describe your problem in the text box\n\n"
                "👈 On the left, you can browse a markdown file containing the description of a constraint problem in natural language"
            )

            # Show placeholder for streaming
            if st.session_state.get("show_streaming_placeholder", True):
                st.markdown("### 🔄 Response Preview")
                st.code(
                    "# LLM's response will appear here in real-time...",
                    language="python",
                )

    # Results section
    if "execution_result" in st.session_state:
        st.header("🎯 Execution Results")

        result = st.session_state.execution_result

        # Create columns for results
        result_col1, result_col2 = st.columns([2, 1])

        with result_col1:
            if result["success"]:
                st.success("✅ Code executed successfully!")

                if result["output"]:
                    st.subheader("📊 Solution Output:")
                    # Try to format the output nicely
                    output_lines = result["output"].strip().split("\n")
                    for line in output_lines:
                        if line.strip():
                            if "Solution:" in line or "Result:" in line:
                                st.markdown(f"**{line}**")
                            else:
                                st.text(line)
                else:
                    st.info("Code executed but produced no output.")
            else:
                st.error("❌ Execution failed!")

                if result["error"]:
                    st.subheader("🚨 Error Details:")
                    st.code(result["error"], language="text")

        with result_col2:
            # Execution metrics
            st.subheader("📈 Execution Info")

            # Create metrics
            if result["success"]:
                st.metric("Status", "✅ Success", delta="Solved")
            else:
                st.metric("Status", "❌ Failed", delta="Error")

            # Code length metric
            code_lines = len(result["code"].split("\n"))
            st.metric("Code Lines", code_lines)

            # Show execution time if available (placeholder)
            st.metric("Runtime", "< 1s", delta="Fast")

        # Show detailed execution info in expander
        with st.expander("🔍 Detailed Execution Information"):
            st.json(
                {
                    "success": result["success"],
                    "output_length": len(result["output"]) if result["output"] else 0,
                    "error_present": bool(result["error"]),
                    "code_length": len(result["code"]),
                }
            )

            # Show the actual executed code
            st.subheader("Executed Code:")
            st.code(result["code"], language="python")

    # Real-time streaming demo section
    st.markdown("---")
    st.header("🔄 Real-time generation demo")

    demo_col1, demo_col2 = st.columns([1, 1])

    with demo_col1:
        st.subheader("Try Quick Examples")

        selected_quick = st.selectbox(
            "Quick examples:", ["Select..."] + list(QUICK_EXAMPLE_PROBLEMS.keys())
        )

        if selected_quick != "Select..." and st.button("🚀 Generate Quickly"):
            # st.session_state.show_streaming_placeholder = True
            # Auto-fill and trigger generation

            if selected_quick in QUICK_EXAMPLE_PROBLEMS:
                with st.container():
                    st.markdown("### 🔄 Streaming LLM's Response...")
                    streaming_container = st.container()

                    # Run async streaming in a proper event loop
                    async def run_quick_generation():
                        return await st.session_state.code_generator.generate_csp_code_stream_async(
                            QUICK_EXAMPLE_PROBLEMS[selected_quick], streaming_container
                        )

                    # Execute the async function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        llm_response = loop.run_until_complete(run_quick_generation())

                        extracted_code = st.session_state.extractor.extract_pycsp3_code(
                            llm_response
                        )
                        st.session_state.generated_code = extracted_code
                        st.session_state.llm_response = llm_response

                        st.success("✅ Quick example generated!")
                    finally:
                        loop.close()
