{
  description = "KDE Icon Theme Colorizer - Inject system colors into icon themes";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      nixpkgsFor = forAllSystems (system: import nixpkgs { inherit system; });
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgsFor.${system};
          finalPkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlays.default ];
          };
        in {
          default = pkgs.callPackage ./default.nix { };
          test-colorized = finalPkgs.papirus-icon-theme-colorized { themeVariant = "Papirus-Dark"; };
        });

      overlays.default = final: prev: {
        kde-icon-theme-colorizer = final.callPackage ./default.nix { };

        # 一个辅助函数，用于生成处理过的图标包
        # 用法示例:
        # environment.systemPackages = [
        #   (pkgs.papirus-icon-theme-colorized { themeVariant = "Papirus-Dark"; })
        # ];
        papirus-icon-theme-colorized = { themeVariant ? "Papirus" }:
          final.stdenv.mkDerivation {
            pname = "${final.lib.toLower themeVariant}-colorized";
            version = prev.papirus-icon-theme.version;

            src = prev.papirus-icon-theme;

            nativeBuildInputs = [ self.packages.${final.system}.default ];

            installPhase = ''
              runHook preInstall
              mkdir -p $out/share/icons

              # 找到实际的主题目录进行复制
              if [ -d "share/icons/${themeVariant}" ]; then
                cp -r share/icons/${themeVariant} $out/share/icons/${themeVariant}-Colorized
              else
                echo "Error: Theme variant ${themeVariant} not found."
                exit 1
              fi

              # 确保文件可写以进行处理
              chmod -R u+w $out/share/icons/${themeVariant}-Colorized

              # 运行着色工具 (使用 --yes 参数跳过交互)
              # 注意: 由于 Nix 环境可能没有设置好的 $HOME，脚本可能会遇到某些问题，
              # 但我们的脚本目前只操作传入的目录，应该是安全的。
              kde-icon-colorizer --yes $out/share/icons/${themeVariant}-Colorized

              # 修改 index.theme 使其在 KDE 设置中显示为新名称
              if [ -f "$out/share/icons/${themeVariant}-Colorized/index.theme" ]; then
                sed -i "s/Name=${themeVariant}/Name=${themeVariant}-Colorized/g" $out/share/icons/${themeVariant}-Colorized/index.theme
              fi

              runHook postInstall
            '';
          };
      };

      devShells = forAllSystems (system: {
        default = nixpkgsFor.${system}.mkShell {
          buildInputs = with nixpkgsFor.${system}; [
            (python3.withPackages (ps: with ps; [ ps.tomli ]))
          ];
        };
      });
    };
}
