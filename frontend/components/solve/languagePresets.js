export const LANGUAGE_PRESETS = [
  {
    id: "python",
    label: "Python 3",
    icon: "🐍",
    fallbackTemplate: [
      "def main():",
      "    # TODO: read from stdin and write to stdout",
      "    pass",
      "",
      "if __name__ == \"__main__\":",
      "    main()",
      "",
    ].join("\n"),
  },
  {
    id: "cpp",
    label: "C++17",
    icon: "⚡",
    fallbackTemplate: [
      "#include <bits/stdc++.h>",
      "using namespace std;",
      "",
      "int main() {",
      "    ios::sync_with_stdio(false);",
      "    cin.tie(nullptr);",
      "",
      "    // TODO: read from stdin and write to stdout",
      "    return 0;",
      "}",
      "",
    ].join("\n"),
  },
  {
    id: "java",
    label: "Java 17",
    icon: "☕",
    fallbackTemplate: [
      "import java.io.*;",
      "import java.util.*;",
      "",
      "public class Main {",
      "    public static void main(String[] args) throws Exception {",
      "        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));",
      "        PrintWriter out = new PrintWriter(System.out);",
      "        // TODO: read input via br and write output via out",
      "        out.flush();",
      "    }",
      "}",
      "",
    ].join("\n"),
  },
];

export const getLanguagePreset = (id) =>
  LANGUAGE_PRESETS.find((preset) => preset.id === id) || LANGUAGE_PRESETS[0];
