----------------------------------------------------------------------------------
-- Company: TU-Dresden 
-- Engineer: Ahmad Nimr, Bharath Kumar Singh Muralidhar
-- Create Date: 6/2018
-- Design Name: QAM mapping/demapping 
-- Module Name: qam_map - Behavioral
-- 
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

-- helper functions 
package log is
  function log2(input : integer) return integer;
  function sqrt(inp : integer) return integer;
end log;

package body log is
function log2( input:integer ) return integer is
variable temp,log:integer;
begin
  temp:=input;
  log:=0;
  while (temp /= 1) loop
   temp:=temp/2;
   log:=log+1;
   end loop;
   return log;
  end function log2;

  function sqrt(inp : integer) return integer is
    variable count : integer;
    variable res : integer;
begin
    count := log2(inp);
    count := count/2;
    res := 2 ** count;
    return res;
end function sqrt;

end log;

library IEEE;
library work;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.log.all;

entity qam_map is
-- n denotes the modulation order, 4, 16, 64, 256, 1024, etc..
generic (n : integer :=256);
port (clk : in std_logic;
      reset : in std_logic;
      enable : in std_logic;
      index : in std_logic_vector((log2(n)-1) downto 0);
      gray_code : in std_logic;
      i_cmp : out std_logic_vector((log2(n)/2) downto 0);
      q_cmp : out std_logic_vector((log2(n)/2) downto 0)
      );
end qam_map;

architecture Behavioral of qam_map is
--Gray to Binary conversion
function gtob (gray : in std_logic_vector(((log2(n)-2)/2) downto 0))
return integer is
    variable bin : std_logic_vector(((log2(n)-2)/2) downto 0);
    variable intg : integer range 0 to 15;
 begin
    bin(((log2(n)-2)/2)) := gray(((log2(n)-2)/2));
    for j in (((log2(n)-4)/2)) downto 0 loop
        bin(j) := bin(j+1) xor gray(j);
    end loop;
    intg := to_integer(unsigned(bin(((log2(n)-2)/2) downto 0)));
    return intg;
end;
-- Binary to integer mapper, equivalent to PAM ,mapping
function mapp( indx: in std_logic_vector(((log2(n)-2)/2) downto 0);             
                     g_c : in std_logic )
return std_logic_vector is  
    variable comp : integer range -15 to 15;
    variable comp_std : std_logic_vector((log2(n)/2) downto 0);
    variable i : integer range 0 to 15;
begin
-- When the input index is in Gray format, it is converted to binary prior to mapping   
    if(g_c = '1') then
            i := gtob(indx(((log2(n)-2)/2) downto 0)); 
    else 
            i := to_integer(unsigned(indx(((log2(n)-2)/2) downto 0)));
    end if;
-- compute the corresponding integer value 	
     comp := (2 * i) - ((sqrt(n))-1);
     comp_std := std_logic_vector(to_signed(comp, ((log2(n)/2)+1)));
     return comp_std;      
end;

begin
   
    process (clk,reset,enable) begin
        if(enable = '1') then
            if (reset = '1') then
                i_cmp <= (others => '0');
                q_cmp <= (others => '0');
            elsif (clk'event and clk='1') then 
-- QAM mapping, the MSB bits corresponds to I and the LSB bits corresponding to Q 
-- Do PAM mapping per component
                i_cmp <= mapp(index((log2(n)-1) downto (log2(n)/2)),gray_code);
                q_cmp <= mapp(index(((log2(n)-2)/2) downto 0),gray_code);   
            end if;
        end if;
    end process;  
end Behavioral;