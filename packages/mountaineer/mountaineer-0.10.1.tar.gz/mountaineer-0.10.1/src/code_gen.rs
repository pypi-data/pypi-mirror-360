/*
 * Construct our js entrypoints that bundle layouts and
 * the downstream pages together. These entrypoints form the actual
 * React component that is mounted on the page.
*/

pub fn build_entrypoint(
    path_group: &[String],
    is_server: bool,
    live_reload_import: &str,
) -> String {
    // Generate the synthetic entrypoint content
    let mut entrypoint_content = String::from("import React from 'react';\n");
    entrypoint_content += &format!("import mountLiveReload from '{live_reload_import}';\n\n");

    for (j, path) in path_group.iter().enumerate() {
        entrypoint_content += &format!("import Layout{j} from '{path}';\n");
    }

    entrypoint_content += "\nconst Entrypoint = () => {\n";
    entrypoint_content += "    mountLiveReload({SSR_RENDERING: process.env.SSR_RENDERING, NODE_ENV: process.env.NODE_ENV, LIVE_RELOAD_PORT: process.env.LIVE_RELOAD_PORT});\n";
    entrypoint_content += "    return (\n";

    // Nest the layouts
    for (i, _path) in path_group.iter().enumerate() {
        entrypoint_content += &"        ".repeat(i + 1);
        entrypoint_content += &format!("<Layout{i}>\n");
    }

    // Close the nested layouts
    for (i, _path) in path_group.iter().enumerate().rev() {
        entrypoint_content += &"        ".repeat(i + 1);
        entrypoint_content += &format!("</Layout{i}>\n");
    }

    entrypoint_content += "    );\n";
    entrypoint_content += "};\n\n";

    // Add client-side or server-side specific code
    if !is_server {
        entrypoint_content += "import { hydrateRoot } from 'react-dom/client';\n";
        entrypoint_content += "const container = document.getElementById('root');\n";
        entrypoint_content += "hydrateRoot(container, <Entrypoint />);\n";
    } else {
        entrypoint_content += "import { renderToString } from 'react-dom/server.edge';\n";
        entrypoint_content += "export const Index = () => renderToString(<Entrypoint />);\n";
    }

    entrypoint_content
}
